"""
Session state management for DealSense AI.
Manages simulation progress, transcript storage, and phase transitions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import time
import uuid


class SimulationPhase(str, Enum):
    SETUP = "setup"
    SIMULATION = "simulation"
    EVALUATION = "evaluation"
    COMPLETE = "complete"


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}


@dataclass
class SessionState:
    """
    Complete session state for one simulation run.
    This is the single source of truth for simulation progress.
    """

    # Identifiers
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Configuration
    persona: str = "CFO"
    industry: str = "technology"
    deal_size: str = "enterprise"
    competitor_mode: bool = False

    # Phase management
    phase: SimulationPhase = SimulationPhase.SETUP

    # Conversation
    messages: List[Message] = field(default_factory=list)
    objections_raised: List[str] = field(default_factory=list)
    objection_types_encountered: List[str] = field(default_factory=list)

    # Stage tracking
    current_stage: str = "discovery"
    stage_history: List[str] = field(default_factory=list)

    # Sentiment tracking
    sentiment_score: float = 0.2  # Start skeptical
    sentiment_history: List[float] = field(default_factory=list)

    # Simulation limits
    max_objections: int = 6
    objection_count: int = 0

    # Evaluation
    scorecard: Optional[Dict] = None
    evaluation_context: Optional[Dict] = None

    # Retrieval cache
    retrieval_cache: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Dict = None) -> None:
        """Add a message to the conversation history."""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history in LangChain/Anthropic format."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
            if m.role in ("user", "assistant")
        ]

    def get_buyer_messages(self) -> List[str]:
        """Get only buyer (assistant) messages for sentiment analysis."""
        return [
            m.content for m in self.messages if m.role == "assistant"
        ]

    def get_transcript(self) -> str:
        """Format full conversation as a readable transcript."""
        lines = [
            f"SIMULATION TRANSCRIPT",
            f"Persona: {self.persona} | Industry: {self.industry} | "
            f"Deal Size: {self.deal_size}",
            f"Stages traversed: {' → '.join(self.stage_history or [self.current_stage])}",
            f"Total exchanges: {len([m for m in self.messages if m.role == 'user'])}",
            "=" * 60,
            "",
        ]
        role_labels = {
            "user": "SALES REP",
            "assistant": self.persona.upper(),
        }
        for msg in self.messages:
            if msg.role in role_labels:
                label = role_labels[msg.role]
                lines.append(f"[{label}]: {msg.content}")
                lines.append("")
        return "\n".join(lines)

    def record_objection(self, objection_text: str, objection_type: str) -> None:
        """Record an objection, avoiding exact duplicates."""
        # Use first 80 chars as dedup key
        key = objection_text[:80]
        if key not in self.objections_raised:
            self.objections_raised.append(key)
            self.objection_count += 1
        if objection_type not in self.objection_types_encountered:
            self.objection_types_encountered.append(objection_type)

    def update_stage(self, new_stage: str) -> None:
        """Update deal stage and record history."""
        if new_stage != self.current_stage:
            self.stage_history.append(new_stage)
            self.current_stage = new_stage

    def update_sentiment(self, new_score: float) -> None:
        """Update sentiment score and record history."""
        self.sentiment_score = new_score
        self.sentiment_history.append(new_score)

    def should_end_simulation(self) -> tuple[bool, str]:
        """
        Check if simulation should end and why.
        Returns (should_end, reason).
        """
        if self.objection_count >= self.max_objections:
            return True, f"Maximum objections reached ({self.max_objections})"
        if self.current_stage == "closing":
            return True, "Closing stage reached"
        if self.sentiment_score >= 0.85:
            return True, "High persuasion score achieved"
        return False, ""

    def transition_to_evaluation(self) -> None:
        """Transition simulation to evaluation phase."""
        self.phase = SimulationPhase.EVALUATION
        if self.current_stage not in self.stage_history:
            self.stage_history.append(self.current_stage)

    def set_scorecard(self, scorecard: Dict) -> None:
        """Store completed scorecard and mark simulation complete."""
        self.scorecard = scorecard
        self.phase = SimulationPhase.COMPLETE

    def get_progress_pct(self) -> float:
        """Get simulation completion percentage."""
        return min(1.0, self.objection_count / self.max_objections)


def init_session_state(
    persona: str,
    industry: str,
    deal_size: str,
    competitor_mode: bool,
    max_objections: int = 6,
) -> SessionState:
    """Initialize a fresh session state with given configuration."""
    state = SessionState(
        persona=persona,
        industry=industry,
        deal_size=deal_size,
        competitor_mode=competitor_mode,
        max_objections=max_objections,
        phase=SimulationPhase.SIMULATION,
        stage_history=["discovery"],
    )
    return state
