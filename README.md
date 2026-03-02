# DealSense AI (Ollama Edition)

**Enterprise Sales Intelligence & Negotiation Simulator**  
*Runs 100% locally — no API keys, no cloud, no cost per token.*

---

## Prerequisites

1. **[Ollama](https://ollama.com)** installed and running
2. A compatible Ollama model pulled (phi3:mini recommended for 8GB RAM)
3. Python 3.10+

---

## Quick Start
> If you only have 8GB RAM, use `phi3:mini`. Larger models may cause slowdowns or crashes.

### 1. Install Ollama & pull a model

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a recommended model (pick one)
ollama pull phi3:mini       # Best overall — recommended
ollama pull mistral         # Fast, strong reasoning
ollama pull gemma2          # Good instruction following

# Start Ollama server (if not already running)
ollama serve
```

### 2. Install Python dependencies

```bash
cd dealsense_ai
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env if needed — defaults work out of the box with Ollama running locally
```

`.env` defaults:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_OBJECTIONS=6
```

### 4. Run

```bash
streamlit run app.py
```

The app auto-detects all models available in your local Ollama instance and lets you pick one from the sidebar. On first run it builds FAISS indexes (~30s). Subsequent runs load from `.cache/`.

---

## Model Recommendations

| Model | Size | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| `phi3:mini` | 3.8B | ⭐⭐⭐ | Very Fast | 8GB laptops (Recommended Default) |
| `llama3` | 8B | ⭐⭐⭐⭐ | Fast | Better reasoning |
| `mistral` | 7B | ⭐⭐⭐⭐ | Very Fast | Strong structured output |
| `gemma2` | 9B | ⭐⭐⭐⭐ | Fast | Instruction following |

> **Note:** `phi3:mini` is the safest choice for 8GB RAM machines.
> Larger models (`llama3`, `mistral`) tend to follow structured JSON instructions more reliably than smaller models like `phi3:mini`.

> **Evaluation quality note:** The forensic scorecard requires structured JSON output. Larger models (llama3.1, mistral) follow this instruction much more reliably than smaller models. The app includes a JSON extraction fallback for models that add preamble.

---

## Architecture

### What Changed from Anthropic Version

| Component | Anthropic Version | Ollama Version |
|-----------|------------------|----------------|
| LLM Client | `anthropic.Anthropic()` | `ollama.Client()` |
| API auth | `ANTHROPIC_API_KEY` | None required |
| Model config | `CLAUDE_MODEL` env var | `OLLAMA_MODEL` env var + UI picker |
| Inference | Cloud API | Local HTTP (`/api/chat`) |
| `ScoringEngineTool` | Takes `claude_client` | Takes `llm_callable` (backend-agnostic) |

### What Stayed the Same

- Dual FAISS indexes (simulation + evaluation — separate retrievers)
- All 5 tool definitions
- Both system prompts (simulation persona enforcement + evaluation forensics)
- Session state management
- Hybrid retrieval with metadata filtering
- Streamlit UI and scorecard rendering

---

## Troubleshooting

**"Ollama not reachable"** — Run `ollama serve` in a terminal and keep it open.

**Evaluation JSON parse fails** — Switch to a larger/smarter model (llama3.1 > mistral > gemma2). The app has a fallback extractor that tries to find JSON in messy output.

**Slow responses** — Normal for local models. `llama3` on CPU may take ~20–60s per turn depending on hardware.
`phi3:mini` typically responds within 5–20s on 8GB machines.

**Force index rebuild** — Delete the `.cache/` directory and restart.
