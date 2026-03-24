"""
Simulation engine: orchestrates buyer persona responses using Ollama.
"""

import os
from typing import Tuple
import ollama

from prompts.system_prompts import build_simulation_prompt
from utils.session import SessionState
from tools.tools import SimulationRetrievalTool, StageManagerTool, SentimentTrackerTool
from rag.pipeline import HybridRetriever

OBJECTION_KEYWORDS = {
    "budget": ["price", "cost", "expensive", "budget", "cheaper", "afford", "discount", "roi"],
    "security": ["security", "compliance", "hipaa", "fedramp", "gdpr", "privacy", "breach", "encryption"],
    "technical_architecture": ["architecture", "scalability", "api", "latency", "performance", "infrastructure"],
    "vendor_lock_in": ["lock-in", "proprietary", "switch", "migrate", "portability", "exit", "format"],
    "implementation_risk": ["implementation", "timeline", "delay", "risk", "late", "on-time", "rollout"],
    "competitive": ["competitor", "alternative", "techforce", "nexus", "other vendor", "compared to"],
    "price_discount": ["discount", "10%", "15%", "20%", "lower", "match", "beat"],
}


def infer_objection_type(text: str) -> str:
    text_lower = text.lower()
    scores = {k: sum(1 for kw in v if kw in text_lower) for k, v in OBJECTION_KEYWORDS.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"


def _call_ollama(system_prompt: str, messages: list, model: str, host: str) -> str:
    client = ollama.Client(host=host)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat(
        model=model,
        messages=full_messages,
        options={"temperature": 0.7, "num_predict": 512},
    )
    return response["message"]["content"].strip()


class SimulationEngine:
    def __init__(self, sim_retriever, sim_retrieval_tool, stage_manager, sentiment_tracker, model=None, host=None):
        self.sim_retriever = sim_retriever
        self.sim_retrieval_tool = sim_retrieval_tool
        self.stage_manager = stage_manager
        self.sentiment_tracker = sentiment_tracker
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def generate_opener(self, state: SessionState) -> str:
        context = self.sim_retrieval_tool.run(
            persona=state.persona, industry=state.industry, deal_size=state.deal_size,
            stage=state.current_stage, objection_focus="opening introduction skepticism",
            session_id=state.session_id,
        ).data.get("context", "")

        system_prompt = build_simulation_prompt(
            persona=state.persona, industry=state.industry, deal_size=state.deal_size,
            current_stage=state.current_stage, objections_raised=state.objections_raised,
            retrieved_context=context,
        )
        return _call_ollama(system_prompt, [{"role": "user", "content":
            "Start the negotiation. Introduce yourself briefly (role only), then open with "
            "your first skeptical challenge. Be direct and professional."}],
            self.model, self.host)

    def generate_buyer_response(self, state: SessionState, user_message: str) -> Tuple[str, bool]:
        objection_focus = self._objection_focus(state)
        context = self.sim_retrieval_tool.run(
            persona=state.persona, industry=state.industry, deal_size=state.deal_size,
            stage=state.current_stage, objection_focus=objection_focus,
            session_id=state.session_id,
        ).data.get("context", "")

        system_prompt = build_simulation_prompt(
            persona=state.persona, industry=state.industry, deal_size=state.deal_size,
            current_stage=state.current_stage, objections_raised=state.objections_raised,
            retrieved_context=context,
        )
        messages = state.get_conversation_history() + [{"role": "user", "content": user_message}]
        buyer_response = _call_ollama(system_prompt, messages, self.model, self.host)

        self._update_state(state, user_message, buyer_response)
        should_end, _ = state.should_end_simulation()
        return buyer_response, should_end

    def _objection_focus(self, state: SessionState) -> str:
        stage_map = {
            "discovery": "roi budget financial justification",
            "technical_review": "security architecture scalability compliance",
            "negotiation": "price discount competitive alternatives",
            "legal_review": "vendor lock-in implementation risk contract terms",
            "closing": "final conditions approval process",
        }
        base = stage_map.get(state.current_stage, "general concerns")
        return base + " competitor comparison" if state.competitor_mode else base

    def _update_state(self, state: SessionState, user_msg: str, buyer_response: str) -> None:
        state.record_objection(buyer_response, infer_objection_type(buyer_response))
        sentiment = self.sentiment_tracker.run(
            buyer_messages=state.get_buyer_messages(),
            current_sentiment_score=state.sentiment_score,
        )
        state.update_sentiment(sentiment.data["sentiment_score"])

        all_msgs = state.get_conversation_history() + [
            {"role": "user", "content": user_msg}
        ]
        stage = self.stage_manager.run(
            current_stage=state.current_stage, conversation_history=all_msgs,
            objections_raised=state.objections_raised, sentiment_score=state.sentiment_score,
        )
        if stage.data.get("advanced"):
            state.update_stage(stage.data["current_stage"])
