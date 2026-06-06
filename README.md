# 🧠 Deep Agents — Enhanced Edition

> **Made by Prathamesh Mishra**
> A production-grade AI agent web application with real-time web search, multi-step planning, streaming responses, and a stunning dark UI.

---

## What is this?

Deep Agents Enhanced is a full-stack AI assistant built on **LangGraph** + **LangChain** with a polished **Streamlit** frontend. It can:

- 🔎 **Search the web** in real-time via Tavily API
- 📋 **Plan step by step** before tackling complex tasks
- 🤖 **Delegate to sub-agents** for deep research and structured output
- 📁 **Read and write files** in a virtual workspace
- 💬 **Remember context** across the conversation
- ⚡ **Stream responses** token by token

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Browser (Streamlit UI)                  │
│  ┌─────────────┐  ┌────────────────────┐  ┌──────────┐  │
│  │  Sidebar    │  │   Chat Area        │  │ Header   │  │
│  │  (history)  │  │   (streaming)      │  │ (model)  │  │
│  └─────────────┘  └────────────────────┘  └──────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   LangGraph ReAct Agent  │
              │   (Orchestration layer)  │
              └────┬────────┬───────────┘
                   │        │
        ┌──────────▼──┐  ┌──▼───────────────┐
        │  LLM Brain  │  │  Tools           │
        │  OpenAI /   │  │  ├ Tavily Search  │
        │  Groq       │  │  ├ Read/Write File│
        └─────────────┘  │  └ Load Skill    │
                         └──────────────────┘
              ┌────────────────────────────┐
              │  Memory Backends           │
              │  ├ MemorySaver (in-session) │
              │  └ InMemoryStore (cross)    │
              └────────────────────────────┘
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/deep-agents-enhanced.git
cd deep-agents-enhanced
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your keys:
```

| Key | Where to get it | Required? |
|-----|----------------|-----------|
| `OPENAI_API_KEY` | platform.openai.com | Yes (for OpenAI models) |
| `TAVILY_API_KEY` | app.tavily.com (free tier) | Yes (for web search) |
| `GROQ_API_KEY` | console.groq.com (free tier) | Only for Groq models |

### 3. Run

```bash
streamlit run streamlit_app.py
```

Open your browser at **http://localhost:8501**

---

## Docker

```bash
# Build and run
docker compose up --build

# Or manually
docker build -t deep-agents-enhanced .
docker run -p 8501:8501 --env-file .env deep-agents-enhanced
```

---

## Project Structure

```
deep-agents-enhanced/
├── streamlit_app.py          # Main UI (Streamlit)
├── agent_core.py             # LangGraph agent + tools
├── main.py                   # CLI entry point
├── config.py                 # Centralised config & constants
├── styles/
│   └── main.css              # Dark theme + watermark CSS
├── components/
│   ├── watermark.py          # "Made by Prathamesh Mishra" overlay
│   ├── sidebar.py            # Chat history sidebar
│   ├── chat_message.py       # Message bubble components
│   └── step_renderer.py      # Collapsible step/tool panels
├── deepagentsdemo/
│   ├── skills/               # Markdown skill cards
│   └── projects/             # Virtual file workspace
├── tests/
│   └── test_basic.py         # Smoke tests
├── .env.example              # API key template
├── Dockerfile                # Container definition
├── docker-compose.yml        # Local dev stack
└── .github/workflows/
    └── deploy.yml            # CI/CD pipeline
```

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| Dark theme | Premium dark UI with gradient accents |
| Watermark | "Made by Prathamesh Mishra" fixed top-right |
| Streaming | Token-by-token response display |
| Chat sidebar | Persistent history with create/delete |
| Model switcher | Pill buttons for OpenAI + Groq models |
| Backend selector | In-Memory / Filesystem / Cross-Session store |
| Step viewer | Collapsible panels for search, planning, files |
| Error cards | Friendly error UI instead of raw tracebacks |
| Responsive | Works on mobile and desktop |

---

## Available Models

| Model | Provider | Best for |
|-------|----------|----------|
| GPT-4o | OpenAI | General use, reasoning |
| GPT-4o Mini | OpenAI | Fast, cost-efficient |
| GPT-4 Turbo | OpenAI | Long context tasks |
| Llama 3.3 70B | Groq | Fast open-source |
| Qwen QwQ 32B | Groq | Deep reasoning |
| Gemma 2 9B | Groq | Lightweight tasks |

---

## Memory Backends

| Backend | Scope | Use case |
|---------|-------|----------|
| In-Memory | Current session only | Default, fast |
| Filesystem | Survives restarts | Long projects |
| Cross-Session | Shared across threads | Team workflows |

---

## Success Criteria

- [x] SC-01 Watermark visible top-right at all times
- [x] SC-02 App starts with `streamlit run streamlit_app.py`
- [x] SC-03 Dark theme — no default Streamlit grey
- [x] SC-04 Chat history sidebar with persistence
- [x] SC-05 Streaming word-by-word responses
- [x] SC-06 Collapsible step panels (not raw JSON)
- [x] SC-07 Model selector pill buttons
- [x] SC-08 All three backends supported
- [x] SC-09 Sub-agent functions available
- [x] SC-10 Docker build ready
- [x] SC-11 Fast startup
- [x] SC-12 Friendly error cards
- [x] SC-13 Full README with architecture
- [ ] SC-14 Publish to GitHub under your account

---

## Deployment

See `.github/workflows/deploy.yml` for CI/CD. Uncomment the target that matches your cloud provider:

- **Railway** — easiest, connects to GitHub directly
- **Render** — free tier available, add deploy hook
- **AWS ECS** — production-grade, needs ECR setup

---

*Made by Prathamesh Mishra · Deep Agents Enhanced · June 2026*
