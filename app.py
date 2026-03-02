"""
DealSense AI - Main Streamlit Application
Enterprise Sales Intelligence & Negotiation Simulator
"""

import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
import ollama

load_dotenv()

# ── Page config must be first ──────────────────────────────────────────────
st.set_page_config(
    page_title="DealSense AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ──────────────────────────────────────────────
from rag.pipeline import build_vector_stores, HybridRetriever
from tools.tools import initialize_tools
from utils.session import SessionState, SimulationPhase, init_session_state
from utils.simulation_engine import SimulationEngine
from utils.evaluation_engine import EvaluationEngine


# ──────────────────────────────────────────────────────────────────────────
# INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Building knowledge base indexes...")
def load_system():
    """Load and cache all system resources (vector stores, tools, engines)."""
    sim_store, eval_store = build_vector_stores()

    sim_retriever = HybridRetriever(sim_store, top_k=5)
    eval_retriever = HybridRetriever(eval_store, top_k=4)

    tools = initialize_tools(sim_retriever, eval_retriever)

    model = os.getenv("OLLAMA_MODEL", "phi3:mini")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    sim_engine = SimulationEngine(
        sim_retriever=sim_retriever,
        sim_retrieval_tool=tools["simulation_retrieval"],
        stage_manager=tools["stage_manager"],
        sentiment_tracker=tools["sentiment_tracker"],
        model=model,
        host=host,
    )

    eval_engine = EvaluationEngine(
        eval_retriever=eval_retriever,
        eval_retrieval_tool=tools["evaluation_retrieval"],
        scoring_engine=tools["scoring_engine"],
        model=model,
        host=host,
    )

    return sim_engine, eval_engine, tools


# ──────────────────────────────────────────────────────────────────────────
# CSS STYLING
# ──────────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .main-header h1 { color: #e94560; margin: 0; font-size: 2.2rem; }
        .main-header p { color: #a8b2d8; margin: 0.5rem 0 0 0; font-size: 1rem; }

        .stage-badge {
            display: inline-block;
            background: #0f3460;
            color: #e94560;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid #e94560;
        }

        .chat-bubble-rep {
            background: #1e3a5f;
            color: #d0e7ff;
            padding: 12px 16px;
            border-radius: 12px 12px 12px 2px;
            margin: 8px 0;
            border-left: 3px solid #4a9eff;
        }
        .chat-bubble-buyer {
            background: #2d1a1a;
            color: #ffd0d0;
            padding: 12px 16px;
            border-radius: 12px 12px 2px 12px;
            margin: 8px 0;
            border-left: 3px solid #e94560;
        }
        .chat-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            opacity: 0.7;
        }

        .score-card {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .score-excellent { color: #10b981; }
        .score-good { color: #34d399; }
        .score-average { color: #f59e0b; }
        .score-poor { color: #ef4444; }

        .progress-bar-container {
            background: #1f2937;
            border-radius: 10px;
            height: 8px;
            margin: 4px 0;
        }
        .verdict-won { color: #10b981; font-weight: 700; font-size: 1.1rem; }
        .verdict-lost { color: #ef4444; font-weight: 700; font-size: 1.1rem; }
        .verdict-uncertain { color: #f59e0b; font-weight: 700; font-size: 1.1rem; }

        .sidebar-section { border-top: 1px solid #374151; padding-top: 1rem; margin-top: 1rem; }

        div[data-testid="stChatInput"] { border-top: 2px solid #e94560 !important; }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────

def render_sidebar(state: Optional[SessionState]) -> dict:
    """Render sidebar with configuration and status."""
    with st.sidebar:
        st.markdown("## 🎯 DealSense AI")
        st.markdown("*Enterprise Negotiation Simulator*")

        config_disabled = state is not None and state.phase != SimulationPhase.SETUP

        st.markdown("### ⚙️ Simulation Setup")

        # Ollama connection + model picker
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            _client = ollama.Client(host=ollama_host)
            available_models = [m["name"] for m in _client.list()["models"]]
            if not available_models:
                available_models = ["llama3", "phi3:mini"]
            st.success(f"✅ Ollama connected ({len(available_models)} model{'s' if len(available_models) != 1 else ''})")
        except Exception:
            available_models = ["phi3:mini", "llama3", "mistral", "gemma2"]
            # st.warning("⚠️ Ollama not reachable. Start with `ollama serve`.")

        default_model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        default_idx = available_models.index(default_model) if default_model in available_models else 0

        selected_model = st.selectbox(
            "Ollama Model",
            available_models,
            index=default_idx,
            disabled=config_disabled,
            help="Recommended: phi3:mini, mistral, or gemma2 (8B+)",
        )
        # Store chosen model in env for engines to pick up
        os.environ["OLLAMA_MODEL"] = selected_model

        persona = st.selectbox(
            "Buyer Persona",
            ["CFO", "CTO", "procurement"],
            disabled=config_disabled,
            help="CFO = Finance focus | CTO = Technical focus | Procurement = Price/contract focus",
        )

        industry = st.selectbox(
            "Industry",
            [
                "technology", "financial_services", "healthcare",
                "manufacturing", "retail", "government", "education",
            ],
            disabled=config_disabled,
        )

        deal_size = st.selectbox(
            "Deal Size",
            ["smb", "mid_market", "enterprise"],
            index=2,
            format_func=lambda x: {"smb": "SMB (<$100K)", "mid_market": "Mid-Market ($100K-$1M)", "enterprise": "Enterprise (>$1M)"}[x],
            disabled=config_disabled,
        )

        competitor_mode = st.toggle(
            "Competitor Mode",
            value=False,
            disabled=config_disabled,
            help="Buyer will reference specific competitors (TechForce, Nexus)",
        )

        max_objections = st.slider(
            "Max Objections",
            min_value=3,
            max_value=10,
            value=6,
            disabled=config_disabled,
            help="Simulation ends after this many buyer objections",
        )

        # Status panel
        if state and state.phase != SimulationPhase.SETUP:
            st.markdown("---")
            st.markdown("### 📊 Live Status")

            # Stage
            stage_labels = {
                "discovery": "🔍 Discovery",
                "technical_review": "🔧 Technical Review",
                "negotiation": "💰 Negotiation",
                "legal_review": "⚖️ Legal Review",
                "closing": "🤝 Closing",
            }
            stage_label = stage_labels.get(state.current_stage, state.current_stage)
            st.markdown(f"**Stage:** {stage_label}")

            # Progress
            progress = state.get_progress_pct()
            st.progress(progress, text=f"Objections: {state.objection_count}/{state.max_objections}")

            # Phase indicator
            phase_icons = {
                SimulationPhase.SIMULATION: "🟢 Simulation Active",
                SimulationPhase.EVALUATION: "🟡 Evaluating...",
                SimulationPhase.COMPLETE: "✅ Complete",
            }
            st.info(phase_icons.get(state.phase, ""))

            if state.phase == SimulationPhase.COMPLETE and state.scorecard:
                st.markdown("---")
                st.markdown("### 🏆 Quick Scores")
                scores = state.scorecard.get("scores", {})
                for key, label in [
                    ("communication_clarity", "Clarity"),
                    ("objection_handling", "Objections"),
                    ("pricing_defense", "Pricing"),
                    ("deal_outcome_probability", "Win Prob"),
                ]:
                    score = scores.get(key, {}).get("score", 0)
                    color = "🟢" if score >= 7 else ("🟡" if score >= 5 else "🔴")
                    st.markdown(f"{color} **{label}**: {score}/10")

    return {
        "persona": persona,
        "industry": industry,
        "deal_size": deal_size,
        "competitor_mode": competitor_mode,
        "max_objections": max_objections,
    }


# ──────────────────────────────────────────────────────────────────────────
# CHAT RENDERING
# ──────────────────────────────────────────────────────────────────────────

def render_chat(state: SessionState):
    """Render chat messages with styled bubbles."""
    persona_label = {
        "CFO": "CFO 💼",
        "CTO": "CTO 💻",
        "procurement": "Procurement 📋",
    }.get(state.persona, state.persona)

    for msg in state.messages:
        if msg.role == "user":
            with st.container():
                st.markdown(
                    f'<div class="chat-bubble-rep">'
                    f'<div class="chat-label">Sales Rep 👔</div>'
                    f'{msg.content}</div>',
                    unsafe_allow_html=True,
                )
        elif msg.role == "assistant":
            with st.container():
                st.markdown(
                    f'<div class="chat-bubble-buyer">'
                    f'<div class="chat-label">{persona_label}</div>'
                    f'{msg.content}</div>',
                    unsafe_allow_html=True,
                )


# ──────────────────────────────────────────────────────────────────────────
# SCORECARD RENDERING
# ──────────────────────────────────────────────────────────────────────────

def render_scorecard(scorecard: dict):
    """Render the evaluation scorecard."""
    st.markdown("---")
    st.markdown("## 📊 Performance Scorecard")

    # Verdict
    outcome = scorecard.get("deal_outcome_prediction", "uncertain")
    confidence = scorecard.get("outcome_confidence", 0.5)
    verdict_class = f"verdict-{outcome}"
    verdict_icons = {"won": "🏆", "lost": "❌", "uncertain": "⚠️"}
    verdict_icon = verdict_icons.get(outcome, "⚠️")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Deal Prediction: {verdict_icon} ")
        st.markdown(
            f'<span class="{verdict_class}">{outcome.upper()}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        st.metric("Confidence", f"{int(confidence * 100)}%")
    with col3:
        scores = scorecard.get("scores", {})
        avg_score = (
            sum(v.get("score", 0) for v in scores.values()) / max(len(scores), 1)
            if scores else 0
        )
        st.metric("Average Score", f"{avg_score:.1f}/10")

    st.markdown(f"**Assessment:** {scorecard.get('overall_assessment', '')}")

    # Score breakdown
    st.markdown("### 📈 Dimension Scores")
    score_cols = st.columns(5)
    score_labels = {
        "communication_clarity": "Clarity",
        "objection_handling": "Objections",
        "competitive_positioning": "Competitive",
        "pricing_defense": "Pricing",
        "deal_outcome_probability": "Win Prob",
    }

    for i, (key, label) in enumerate(score_labels.items()):
        score_data = scores.get(key, {})
        score = score_data.get("score", 0)
        color = "normal" if score >= 7 else ("off" if score >= 5 else "inverse")
        with score_cols[i]:
            st.metric(label, f"{score}/10")

    # Detailed breakdown
    st.markdown("### 🔍 Detailed Analysis")
    for key, label in score_labels.items():
        score_data = scores.get(key, {})
        score = score_data.get("score", 0)

        with st.expander(f"{label}: {score}/10", expanded=(score < 6)):
            if score_data.get("evidence_quote"):
                st.markdown(f"**📝 Evidence Quote:**")
                st.info(f'"{score_data["evidence_quote"]}"')
            if score_data.get("benchmark_comparison"):
                st.markdown(f"**📊 vs. Winning Pattern:**")
                st.markdown(score_data["benchmark_comparison"])
            if score_data.get("reasoning"):
                st.markdown(f"**💡 Reasoning:**")
                st.markdown(score_data["reasoning"])
            if score_data.get("improvement"):
                st.markdown(f"**🎯 Improvement:**")
                st.success(score_data["improvement"])

    # Turning points
    turning_points = scorecard.get("key_turning_points", [])
    if turning_points:
        st.markdown("### 🔄 Key Turning Points")
        for tp in turning_points:
            impact_icon = "✅" if tp.get("impact") == "positive" else "❌"
            with st.expander(f"{impact_icon} {tp.get('moment', '')}"):
                st.markdown(f"**Rep said:** *\"{tp.get('rep_response', '')}\"*")
                st.markdown(f"**Why it mattered:** {tp.get('explanation', '')}")

    # Strengths and failures
    col_a, col_b = st.columns(2)
    with col_a:
        strengths = scorecard.get("standout_strengths", [])
        if strengths:
            st.markdown("### ✅ Standout Strengths")
            for s in strengths:
                st.success(s)

    with col_b:
        failures = scorecard.get("critical_failures", [])
        if failures:
            st.markdown("### ❌ Critical Failures")
            for f in failures:
                st.error(f)

    # Coaching actions
    actions = scorecard.get("priority_coaching_actions", [])
    if actions:
        st.markdown("### 🎯 Priority Coaching Actions")
        for i, action in enumerate(actions, 1):
            st.markdown(f"**{i}.** {action}")

    # Raw JSON (expandable)
    with st.expander("🔧 Raw Scorecard JSON"):
        st.json(scorecard)


# ──────────────────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────────────────

def main():
    inject_css()

    # Load system resources
    try:
        sim_engine, eval_engine, tools = load_system()
    except Exception as e:
        st.error(f"System initialization failed: {e}")
        st.info("Make sure Ollama is running (`ollama serve`) and your model is pulled (`ollama pull phi3:mini`).")
        st.stop()

    # Initialize session state
    if "session" not in st.session_state:
        st.session_state.session = None
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 DealSense AI</h1>
        <p>Enterprise Sales Intelligence & Negotiation Simulator</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    config = render_sidebar(st.session_state.session)

    # ── SETUP PHASE ──────────────────────────────────────────────────────
    if st.session_state.session is None:
        st.markdown("### 🚀 Ready to Simulate")
        st.markdown(
            "Configure your buyer persona, industry, and deal parameters in the sidebar, "
            "then start the simulation. You'll face a real enterprise buyer—no hints, no help."
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("▶️ Start Simulation", type="primary", use_container_width=True):
                with st.spinner("Initializing simulation..."):
                    state = init_session_state(
                        persona=config["persona"],
                        industry=config["industry"],
                        deal_size=config["deal_size"],
                        competitor_mode=config["competitor_mode"],
                        max_objections=config["max_objections"],
                    )

                    # Generate opener
                    opener = sim_engine.generate_opener(state)
                    state.add_message("assistant", opener)
                    st.session_state.session = state
                    st.rerun()

        # Instructions
        with st.expander("📖 How DealSense AI Works"):
            st.markdown("""
**DealSense AI** is a dual-phase enterprise sales training system.

**Phase 1 — Simulation:**
- You play a sales representative trying to close a deal
- The AI plays a skeptical enterprise buyer (CFO, CTO, or Procurement)
- The buyer will raise realistic objections grounded in historical deal data
- NO hints, NO feedback, NO assistance during simulation
- The simulation ends after max objections are raised or you reach closing

**Phase 2 — Evaluation:**
- After simulation ends, a forensic analysis runs automatically
- Your responses are compared against historically winning and losing patterns
- You receive a structured scorecard with evidence-based scoring
- Specific quotes from your conversation are used as evidence

**Scoring Dimensions:**
1. Communication Clarity
2. Objection Handling
3. Competitive Positioning
4. Pricing Defense
5. Deal Outcome Probability

**Tips:**
- Be specific with numbers and data (buyers hate vague claims)
- Acknowledge objections before responding
- Know your product architecture cold if facing a CTO
- Never concede price immediately; defend value first
            """)

        return

    # Active session
    state: SessionState = st.session_state.session

    # ── SIMULATION PHASE ─────────────────────────────────────────────────
    if state.phase == SimulationPhase.SIMULATION:
        # Stage indicator
        stage_labels = {
            "discovery": "🔍 Discovery",
            "technical_review": "🔧 Technical Review",
            "negotiation": "💰 Negotiation",
            "legal_review": "⚖️ Legal Review",
            "closing": "🤝 Closing",
        }
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            st.markdown(
                f'<span class="stage-badge">{stage_labels.get(state.current_stage, state.current_stage)}</span>',
                unsafe_allow_html=True,
            )
        with col_s2:
            st.progress(state.get_progress_pct())
        with col_s3:
            st.caption(f"Objection {state.objection_count}/{state.max_objections}")

        st.markdown("---")

        # Chat display
        render_chat(state)

        # Input
        user_input = st.chat_input(
            "Your response as sales rep...",
            key=f"chat_input_{st.session_state.input_key}",
        )

        if user_input and user_input.strip():
            # Record user message
            state.add_message("user", user_input.strip())

            with st.spinner("Buyer is responding..."):
                buyer_response, should_end = sim_engine.generate_buyer_response(
                    state, user_input.strip()
                )

            # Record buyer response
            state.add_message("assistant", buyer_response)
            st.session_state.input_key += 1

            if should_end:
                state.transition_to_evaluation()

            st.rerun()

        # End simulation button
        col_e1, col_e2 = st.columns([1, 5])
        with col_e1:
            if st.button("⏹ End & Evaluate", help="End simulation and get your scorecard"):
                state.transition_to_evaluation()
                st.rerun()

    # ── EVALUATION PHASE ─────────────────────────────────────────────────
    elif state.phase == SimulationPhase.EVALUATION:
        render_chat(state)
        st.markdown("---")

        with st.spinner("🔍 Running forensic evaluation... This takes 15-30 seconds."):
            scorecard = eval_engine.run_evaluation(state)

        if scorecard:
            render_scorecard(scorecard)
        else:
            st.error("Evaluation failed. Please check your API key and try again.")

        if st.button("🔄 New Simulation", type="primary"):
            st.session_state.session = None
            st.session_state.input_key = 0
            st.rerun()

    # ── COMPLETE PHASE ───────────────────────────────────────────────────
    elif state.phase == SimulationPhase.COMPLETE:
        render_chat(state)
        if state.scorecard:
            render_scorecard(state.scorecard)

        col_r1, col_r2 = st.columns([1, 4])
        with col_r1:
            if st.button("🔄 New Simulation", type="primary"):
                st.session_state.session = None
                st.session_state.input_key = 0
                st.rerun()
        with col_r2:
            if st.button("📋 Copy Transcript"):
                st.code(state.get_transcript(), language=None)


# ──────────────────────────────────────────────────────────────────────────
from typing import Optional

if __name__ == "__main__":
    main()
