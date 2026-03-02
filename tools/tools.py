"""
Explicit tool definitions for DealSense AI.
Each tool has a clear interface, purpose, and return structure.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class DealStage(str, Enum):
    DISCOVERY = "discovery"
    TECHNICAL_REVIEW = "technical_review"
    NEGOTIATION = "negotiation"
    LEGAL_REVIEW = "legal_review"
    CLOSING = "closing"


class Sentiment(str, Enum):
    HOSTILE = "hostile"
    SKEPTICAL = "skeptical"
    NEUTRAL = "neutral"
    WARMING = "warming"
    POSITIVE = "positive"


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1: Simulation Retrieval Tool
# ─────────────────────────────────────────────────────────────────────────────

class SimulationRetrievalTool:
    """
    Retrieves context to ground buyer objection generation.
    Uses hybrid retrieval: vector search + metadata filtering.
    
    Purpose: Make buyer objections realistic and grounded in historical patterns.
    NOT used during evaluation.
    """

    name = "simulation_retrieval_tool"
    description = (
        "Retrieves persona-specific objections, stage challenges, industry patterns, "
        "and historical deal segments to ground objection generation."
    )

    def __init__(self, retriever):
        self.retriever = retriever
        self._cache: Dict[str, str] = {}

    def run(
        self,
        persona: str,
        industry: str,
        deal_size: str,
        stage: str,
        objection_focus: str,
        session_id: str,
    ) -> ToolResult:
        """
        Retrieve simulation context for the current scenario.
        
        Args:
            persona: "CFO" | "CTO" | "procurement"
            industry: target industry
            deal_size: "smb" | "mid_market" | "enterprise"
            stage: current deal stage
            objection_focus: what type of objection to generate
            session_id: for caching
        
        Returns:
            ToolResult with formatted context string
        """
        cache_key = f"{session_id}:{persona}:{stage}:{objection_focus}"
        if cache_key in self._cache:
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"context": self._cache[cache_key], "cached": True},
            )

        try:
            from rag.pipeline import format_retrieved_docs
            docs = self.retriever.retrieve_sim_context(
                persona=persona,
                industry=industry,
                deal_size=deal_size,
                stage=stage,
                objection_focus=objection_focus,
            )
            context = format_retrieved_docs(docs, max_chars=1500)
            self._cache[cache_key] = context

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "context": context,
                    "docs_retrieved": len(docs),
                    "cached": False,
                },
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={"context": ""},
                error=str(e),
            )


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2: Evaluation Retrieval Tool
# ─────────────────────────────────────────────────────────────────────────────

class EvaluationRetrievalTool:
    """
    Retrieves benchmarks for forensic evaluation.
    Separate from simulation retriever - uses evaluation-only index.
    
    Purpose: Compare user responses against historically successful and failed patterns.
    ONLY used after simulation ends.
    """

    name = "evaluation_retrieval_tool"
    description = (
        "Retrieves winning deal excerpts, losing deal excerpts, "
        "strong rebuttals, pricing defense scripts, and competitive benchmarks "
        "to enable evidence-based scoring."
    )

    def __init__(self, retriever):
        self.retriever = retriever

    def run(
        self,
        transcript: str,
        objection_types_encountered: List[str],
        persona: str,
    ) -> ToolResult:
        """
        Retrieve evaluation benchmarks for each objection type encountered.
        
        Args:
            transcript: full simulation transcript
            objection_types_encountered: list of objection types in simulation
            persona: buyer persona used
        
        Returns:
            ToolResult with categorized benchmark context
        """
        try:
            from rag.pipeline import format_retrieved_docs
            all_context = {}

            for obj_type in objection_types_encountered[:4]:  # cap at 4 types
                docs_by_type = self.retriever.retrieve_eval_context(
                    user_response=transcript[-2000:],  # recent context
                    objection_type=obj_type,
                    persona=persona,
                )
                all_context[obj_type] = {
                    "winning_patterns": format_retrieved_docs(
                        docs_by_type["winning_patterns"], max_chars=600
                    ),
                    "losing_patterns": format_retrieved_docs(
                        docs_by_type["losing_patterns"], max_chars=400
                    ),
                    "playbook": format_retrieved_docs(
                        docs_by_type["playbook_guidance"], max_chars=500
                    ),
                }

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"benchmarks": all_context},
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={"benchmarks": {}},
                error=str(e),
            )


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3: Stage Manager Tool
# ─────────────────────────────────────────────────────────────────────────────

class StageManagerTool:
    """
    Manages deal stage progression.
    Prevents random stage jumps and enforces logical flow.
    
    Stage order: discovery → technical_review → negotiation → legal_review → closing
    """

    name = "stage_manager_tool"
    description = "Manages deal stage progression based on conversation signals."

    STAGE_ORDER = [
        DealStage.DISCOVERY,
        DealStage.TECHNICAL_REVIEW,
        DealStage.NEGOTIATION,
        DealStage.LEGAL_REVIEW,
        DealStage.CLOSING,
    ]

    # Keywords that trigger stage advancement
    ADVANCEMENT_SIGNALS = {
        DealStage.DISCOVERY: [
            "use case", "requirements", "understand your needs",
            "tell me more", "what problem", "why now"
        ],
        DealStage.TECHNICAL_REVIEW: [
            "architecture", "security", "integration", "api", "compliance",
            "scalability", "infrastructure", "technical"
        ],
        DealStage.NEGOTIATION: [
            "price", "cost", "budget", "discount", "contract", "payment",
            "roi", "value", "investment", "quote"
        ],
        DealStage.LEGAL_REVIEW: [
            "legal", "terms", "liability", "sla", "penalty", "lock-in",
            "portability", "indemnification", "warranty"
        ],
    }

    STAGE_LABELS = {
        "discovery": "🔍 Discovery",
        "technical_review": "🔧 Technical Review",
        "negotiation": "💰 Negotiation",
        "legal_review": "⚖️ Legal Review",
        "closing": "🤝 Closing",
    }

    def run(
        self,
        current_stage: str,
        conversation_history: List[Dict],
        objections_raised: List[str],
        sentiment_score: float,
    ) -> ToolResult:
        """
        Determine if stage should advance based on conversation signals.
        
        Returns new stage and progression status.
        """
        current = DealStage(current_stage)
        current_idx = self.STAGE_ORDER.index(current)

        # Can't advance past closing
        if current == DealStage.CLOSING:
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "current_stage": current.value,
                    "stage_label": self.STAGE_LABELS[current.value],
                    "advanced": False,
                    "can_advance": False,
                },
            )

        # Minimum objections before advancing (prevents premature progression)
        MIN_OBJECTIONS_PER_STAGE = {
            DealStage.DISCOVERY: 1,
            DealStage.TECHNICAL_REVIEW: 1,
            DealStage.NEGOTIATION: 1,
            DealStage.LEGAL_REVIEW: 1,
        }
        min_required = MIN_OBJECTIONS_PER_STAGE.get(current, 1)
        stage_objections = [o for o in objections_raised if current.value in o or True]

        # Check if conversation signals indicate readiness to advance
        recent_text = ""
        for msg in conversation_history[-4:]:
            recent_text += msg.get("content", "").lower() + " "

        next_stage = self.STAGE_ORDER[current_idx + 1]
        next_signals = self.ADVANCEMENT_SIGNALS.get(next_stage, [])
        signal_count = sum(1 for sig in next_signals if sig in recent_text)

        should_advance = (
            len(objections_raised) >= min_required
            and signal_count >= 1
            and sentiment_score > 0.3  # some rapport built
        )

        if should_advance:
            new_stage = next_stage
            advanced = True
        else:
            new_stage = current
            advanced = False

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "current_stage": new_stage.value,
                "stage_label": self.STAGE_LABELS[new_stage.value],
                "previous_stage": current.value,
                "advanced": advanced,
                "stage_index": self.STAGE_ORDER.index(new_stage),
                "total_stages": len(self.STAGE_ORDER),
                "can_advance": new_stage != DealStage.CLOSING,
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 4: Sentiment Tracker Tool
# ─────────────────────────────────────────────────────────────────────────────

class SentimentTrackerTool:
    """
    Tracks buyer sentiment and persuasion indicators throughout simulation.
    
    Sentiment is NOT revealed to the user during simulation.
    Used internally for stage management and end-of-simulation trigger.
    """

    name = "sentiment_tracker_tool"
    description = "Tracks buyer sentiment progression and persuasion indicators."

    # Signals that indicate positive movement
    POSITIVE_SIGNALS = [
        "interesting", "tell me more", "that makes sense", "i see your point",
        "reasonable", "workable", "let's discuss", "we can consider",
        "show me", "walk me through", "what if we", "can you",
        "that addresses", "fair point", "understood"
    ]

    # Signals that indicate resistance
    NEGATIVE_SIGNALS = [
        "non-starter", "not acceptable", "we're done", "that's not what",
        "you don't understand", "i've heard that before", "prove it",
        "that's not good enough", "moving on", "we have alternatives",
        "not convinced", "too expensive", "unacceptable"
    ]

    def run(
        self,
        buyer_messages: List[str],
        current_sentiment_score: float,
    ) -> ToolResult:
        """
        Analyze buyer messages for sentiment signals.
        
        Returns updated sentiment score (0.0 = hostile, 1.0 = positive).
        """
        if not buyer_messages:
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "sentiment_score": current_sentiment_score,
                    "sentiment_label": Sentiment.SKEPTICAL.value,
                    "persuasion_indicators": [],
                    "resistance_indicators": [],
                },
            )

        # Analyze recent messages (last 3)
        recent_text = " ".join(buyer_messages[-3:]).lower()

        positive_count = sum(1 for sig in self.POSITIVE_SIGNALS if sig in recent_text)
        negative_count = sum(1 for sig in self.NEGATIVE_SIGNALS if sig in recent_text)

        # Update score with momentum
        delta = (positive_count * 0.08) - (negative_count * 0.10)
        new_score = max(0.0, min(1.0, current_sentiment_score + delta))

        # Determine label
        if new_score < 0.2:
            label = Sentiment.HOSTILE.value
        elif new_score < 0.4:
            label = Sentiment.SKEPTICAL.value
        elif new_score < 0.6:
            label = Sentiment.NEUTRAL.value
        elif new_score < 0.8:
            label = Sentiment.WARMING.value
        else:
            label = Sentiment.POSITIVE.value

        return ToolResult(
            tool_name=self.name,
            success=True,
            data={
                "sentiment_score": round(new_score, 3),
                "sentiment_label": label,
                "positive_signals_detected": positive_count,
                "negative_signals_detected": negative_count,
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 5: Scoring Engine Tool
# ─────────────────────────────────────────────────────────────────────────────

class ScoringEngineTool:
    """
    Drives the final evaluation scoring after simulation ends.
    Calls Claude with evaluation prompt and retrieved benchmarks.
    
    Returns structured JSON scorecard.
    """

    name = "scoring_engine_tool"
    description = (
        "Analyzes the complete transcript against retrieved benchmarks "
        "and produces a structured JSON scorecard."
    )

    def run(
        self,
        transcript: str,
        evaluation_context: Dict,
        persona: str,
        industry: str,
        llm_callable,
        eval_system_prompt: str,
        model: str,
    ) -> ToolResult:
        """
        Run scoring engine against full transcript.
        
        Args:
            transcript: formatted full conversation transcript
            evaluation_context: retrieved benchmarks from eval retrieval tool
            persona: buyer persona used
            industry: industry context
            llm_callable: callable(system_prompt, user_message) -> str
            eval_system_prompt: evaluation system prompt
            model: Claude model string
        
        Returns:
            ToolResult with parsed scorecard dict
        """
        # Build evaluation prompt with all context
        benchmark_text = self._format_benchmarks(evaluation_context)

        user_message = f"""## SIMULATION TRANSCRIPT
{transcript}

## RETRIEVED EVALUATION BENCHMARKS
{benchmark_text}

## EVALUATION TASK
Evaluate the sales representative's performance in this {persona} negotiation in the {industry} industry.
Produce the structured JSON scorecard as specified in your instructions.
Quote specific lines from the transcript as evidence for each score.
Compare against the retrieved winning and losing patterns above."""

        try:
            # llm_callable is injected by EvaluationEngine — works with any LLM backend
            raw_output = llm_callable(eval_system_prompt, user_message)

            # Parse JSON
            # Handle possible markdown code fences
            if "```json" in raw_output:
                raw_output = raw_output.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_output:
                raw_output = raw_output.split("```")[1].split("```")[0].strip()

            scorecard = json.loads(raw_output)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"scorecard": scorecard, "raw_output": raw_output},
            )
        except json.JSONDecodeError as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={"scorecard": None, "raw_output": raw_output if 'raw_output' in dir() else ""},
                error=f"JSON parse error: {e}",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={"scorecard": None},
                error=str(e),
            )

    def _format_benchmarks(self, evaluation_context: Dict) -> str:
        """Format retrieved benchmarks into readable context."""
        if not evaluation_context:
            return "No benchmarks retrieved."

        parts = []
        benchmarks = evaluation_context.get("benchmarks", {})
        for obj_type, contexts in benchmarks.items():
            parts.append(f"### Objection Type: {obj_type.replace('_', ' ').title()}")
            if contexts.get("winning_patterns"):
                parts.append(f"**Winning Patterns:**\n{contexts['winning_patterns']}")
            if contexts.get("losing_patterns"):
                parts.append(f"**Losing Patterns:**\n{contexts['losing_patterns']}")
            if contexts.get("playbook"):
                parts.append(f"**Playbook Guidance:**\n{contexts['playbook']}")
            parts.append("")

        return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────────────────────────────────────

def initialize_tools(sim_retriever, eval_retriever) -> Dict[str, Any]:
    """Initialize all tools with their dependencies."""
    return {
        "simulation_retrieval": SimulationRetrievalTool(sim_retriever),
        "evaluation_retrieval": EvaluationRetrievalTool(eval_retriever),
        "stage_manager": StageManagerTool(),
        "sentiment_tracker": SentimentTrackerTool(),
        "scoring_engine": ScoringEngineTool(),
    }
