"""
Evaluation engine: orchestrates post-simulation forensic scoring using Ollama.
Separate from simulation — never leaks during active simulation.
"""

import os
import json
from typing import Dict, Optional
import ollama

from prompts.system_prompts import EVALUATION_SYSTEM_PROMPT
from utils.session import SessionState
from tools.tools import EvaluationRetrievalTool, ScoringEngineTool
from rag.pipeline import HybridRetriever


def _call_ollama_eval(system_prompt: str, user_message: str, model: str, host: str) -> str:
    client = ollama.Client(host=host)
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        options={"temperature": 0.2, "num_predict": 3000},
    )
    return response["message"]["content"].strip()


class EvaluationEngine:
    """
    Orchestrates the evaluation phase using a local Ollama model.
    Uses a separate retriever from simulation — evaluation isolation enforced here.
    """

    def __init__(self, eval_retriever, eval_retrieval_tool, scoring_engine, model=None, host=None):
        self.eval_retriever = eval_retriever
        self.eval_retrieval_tool = eval_retrieval_tool
        self.scoring_engine = scoring_engine
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def run_evaluation(self, state: SessionState) -> Optional[Dict]:
        if not state.messages:
            return None

        eval_result = self.eval_retrieval_tool.run(
            transcript=state.get_transcript(),
            objection_types_encountered=state.objection_types_encountered or ["budget"],
            persona=state.persona,
        )
        evaluation_context = eval_result.data if eval_result.success else {"benchmarks": {}}
        state.evaluation_context = evaluation_context

        scorecard = self._run_scoring(state, evaluation_context)
        state.set_scorecard(scorecard)
        return scorecard

    def _run_scoring(self, state: SessionState, evaluation_context: Dict) -> Dict:
        benchmark_text = self._format_benchmarks(evaluation_context)
        transcript = state.get_transcript()

        user_message = f"""## SIMULATION TRANSCRIPT
{transcript}

## RETRIEVED EVALUATION BENCHMARKS
{benchmark_text}

## EVALUATION TASK
Evaluate the sales representative's performance in this {state.persona} negotiation in the {state.industry} industry.
Produce the structured JSON scorecard as specified in your instructions.
Quote specific lines from the transcript as evidence for each score.
Return ONLY valid JSON — no preamble, no explanation, no markdown fences."""

        try:
            raw = _call_ollama_eval(EVALUATION_SYSTEM_PROMPT, user_message, self.model, self.host)

            # Strip markdown fences if present
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            return json.loads(raw)

        except json.JSONDecodeError:
            # Try to extract JSON substring
            try:
                start = raw.index("{")
                end = raw.rindex("}") + 1
                return json.loads(raw[start:end])
            except Exception:
                return self._fallback_scorecard("JSON parse failed — model output was not valid JSON.")
        except Exception as e:
            return self._fallback_scorecard(str(e))

    def _format_benchmarks(self, evaluation_context: Dict) -> str:
        if not evaluation_context:
            return "No benchmarks retrieved."
        parts = []
        for obj_type, contexts in evaluation_context.get("benchmarks", {}).items():
            parts.append(f"### {obj_type.replace('_', ' ').title()}")
            if contexts.get("winning_patterns"):
                parts.append(f"**Winning:**\n{contexts['winning_patterns']}")
            if contexts.get("losing_patterns"):
                parts.append(f"**Losing:**\n{contexts['losing_patterns']}")
            if contexts.get("playbook"):
                parts.append(f"**Playbook:**\n{contexts['playbook']}")
        return "\n\n".join(parts)

    def _fallback_scorecard(self, error: str) -> Dict:
        empty_dim = {"score": 0, "evidence_quote": "N/A", "benchmark_comparison": "N/A",
                     "reasoning": error, "improvement": "Retry evaluation."}
        return {
            "overall_assessment": f"Evaluation error: {error}",
            "deal_outcome_prediction": "uncertain",
            "outcome_confidence": 0.5,
            "scores": {k: empty_dim.copy() for k in [
                "communication_clarity", "objection_handling",
                "competitive_positioning", "pricing_defense", "deal_outcome_probability"
            ]},
            "key_turning_points": [],
            "critical_failures": [error],
            "standout_strengths": [],
            "priority_coaching_actions": ["Check Ollama is running and model is pulled. Retry evaluation."],
        }
