"""
Core agent implementation using LangGraph.
Supports OpenAI and Groq backends with Tavily web search,
file operations, planning, and sub-agent delegation.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Generator

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore


# ── LLM factory ─────────────────────────────────────────────────────────────

def build_llm(model_id: str) -> Any:
    provider, model_name = model_id.split(":", 1) if ":" in model_id else ("openai", model_id)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            streaming=True,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model_name,
            temperature=0.7,
            streaming=True,
            api_key=os.getenv("GROQ_API_KEY"),
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ── Tools ────────────────────────────────────────────────────────────────────

@tool
def tavily_search(query: str) -> str:
    """Search the internet for up-to-date information. Use this for any factual
    questions about recent events, companies, people, or data you're unsure about."""
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = client.search(query=query, max_results=5)
    formatted = []
    for r in results.get("results", []):
        formatted.append(f"**{r.get('title', '')}**\n{r.get('url', '')}\n{r.get('content', '')}")
    return "\n\n---\n\n".join(formatted) or "No results found."


@tool
def read_file(path: str) -> str:
    """Read the contents of a file from the virtual workspace."""
    try:
        workspace = Path("deepagentsdemo/projects")
        safe_path = (workspace / path).resolve()
        if not str(safe_path).startswith(str(workspace.resolve())):
            return "Error: path traversal not allowed."
        return safe_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file in the virtual workspace."""
    try:
        workspace = Path("deepagentsdemo/projects")
        safe_path = (workspace / path).resolve()
        if not str(safe_path).startswith(str(workspace.resolve())):
            return "Error: path traversal not allowed."
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files in the virtual workspace directory."""
    try:
        workspace = Path("deepagentsdemo/projects")
        target = (workspace / directory).resolve()
        if not str(target).startswith(str(workspace.resolve())):
            return "Error: path traversal not allowed."
        if not target.exists():
            return f"Directory not found: {directory}"
        files = [str(p.relative_to(workspace)) for p in target.rglob("*") if p.is_file()]
        return "\n".join(files) if files else "No files found."
    except Exception as e:
        return f"Error listing files: {e}"


@tool
def load_skill(skill_name: str) -> str:
    """Load a skill card (markdown file) from the skills library."""
    skills_dir = Path("deepagentsdemo/skills")
    skill_file = skills_dir / f"{skill_name}.md"
    if skill_file.exists():
        return skill_file.read_text(encoding="utf-8")
    available = [p.stem for p in skills_dir.glob("*.md")]
    return f"Skill '{skill_name}' not found. Available: {', '.join(available) or 'none'}"


# ── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Deep Agent, an advanced AI assistant with planning, research, \
and execution capabilities. You can:

- Search the internet for real-time information using tavily_search
- Read and write files in the workspace using read_file, write_file, list_files
- Load skill cards for specialized tasks using load_skill

When given a complex task:
1. First, outline your plan step by step
2. Execute each step, using tools as needed
3. Synthesise a clear, structured final answer

Be thorough, accurate, and helpful. Always cite sources when using web search results."""


def _load_agents_md() -> str:
    agents_md = Path("AGENTS.md")
    if agents_md.exists():
        return agents_md.read_text(encoding="utf-8")
    return ""


# ── Agent builder ────────────────────────────────────────────────────────────

_agent_cache: dict[str, Any] = {}
_checkpointer = MemorySaver()
_store = InMemoryStore()


def build_agent(model_id: str, backend: str = "memory") -> Any:
    cache_key = f"{model_id}:{backend}"
    if cache_key in _agent_cache:
        return _agent_cache[cache_key]

    llm = build_llm(model_id)
    tools = [tavily_search, read_file, write_file, list_files, load_skill]

    agents_context = _load_agents_md()
    system = SYSTEM_PROMPT
    if agents_context:
        system = f"{agents_context}\n\n{system}"

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=_checkpointer if backend in ("memory", "store") else None,
        store=_store if backend == "store" else None,
        prompt=system,
    )

    _agent_cache[cache_key] = agent
    return agent


# ── Step extraction ──────────────────────────────────────────────────────────

def extract_steps_from_events(events: list[dict]) -> list[dict]:
    steps = []
    for event in events:
        if "tools" in event:
            for msg in event["tools"].get("messages", []):
                if isinstance(msg, ToolMessage):
                    tool_name = getattr(msg, "name", "tool")
                    step_type = "search" if "search" in tool_name.lower() else "file_read" if "read" in tool_name.lower() else "file_write" if "write" in tool_name.lower() else "tool"
                    steps.append({
                        "type": step_type,
                        "tool": tool_name,
                        "output": str(msg.content)[:800],
                    })
        if "agent" in event:
            for msg in event["agent"].get("messages", []):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        name = tc.get("name", "tool")
                        args = tc.get("args", {})
                        if "search" in name.lower():
                            steps.append({"type": "search", "tool": name, "query": args.get("query", ""), "input": str(args)})
                        elif "read" in name.lower():
                            steps.append({"type": "file_read", "tool": name, "path": args.get("path", ""), "input": str(args)})
                        elif "write" in name.lower():
                            steps.append({"type": "file_write", "tool": name, "path": args.get("path", ""), "input": str(args)})
                        else:
                            steps.append({"type": "tool", "tool": name, "input": str(args)})
    return steps


# ── Streaming run ────────────────────────────────────────────────────────────

def stream_agent_response(
    agent: Any,
    user_message: str,
    thread_id: str,
    history: list[dict],
) -> Generator[tuple[str, list[dict]], None, None]:
    """
    Yields (token_chunk, steps_so_far) tuples.
    Caller accumulates tokens and updates UI.
    """
    messages = []
    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    config = {"configurable": {"thread_id": thread_id}}
    steps: list[dict] = []
    collected_events: list[dict] = []

    for event in agent.stream({"messages": messages}, config=config, stream_mode="values"):
        collected_events.append(event)
        new_steps = extract_steps_from_events([event])
        steps.extend(new_steps)

        msgs = event.get("messages", [])
        if msgs:
            last = msgs[-1]
            if isinstance(last, AIMessage) and last.content and not getattr(last, "tool_calls", None):
                yield last.content, steps

    # Also try token-level streaming if available
    return


def run_agent_response(
    agent: Any,
    user_message: str,
    thread_id: str,
    history: list[dict],
) -> tuple[str, list[dict]]:
    """Non-streaming fallback. Returns (full_response, steps)."""
    messages = []
    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_message))

    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": messages}, config=config)

    steps = extract_steps_from_events([result])
    final_messages = result.get("messages", [])
    final_content = ""
    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content:
            final_content = msg.content
            break

    return final_content, steps


# ── Research sub-agent ───────────────────────────────────────────────────────

def research_agent(topic: str, model_id: str = "openai:gpt-4o-mini") -> str:
    """Spin up a specialist research sub-agent for deep dives."""
    llm = build_llm(model_id)
    tools = [tavily_search]
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a research specialist. Search thoroughly and provide comprehensive, cited summaries.",
    )
    result = agent.invoke({"messages": [HumanMessage(content=f"Research this topic comprehensively: {topic}")]})
    msgs = result.get("messages", [])
    for msg in reversed(msgs):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "Research completed but no output returned."


def structured_researcher(query: str, output_format: str, model_id: str = "openai:gpt-4o-mini") -> str:
    """Sub-agent that returns structured JSON output."""
    llm = build_llm(model_id)
    tools = [tavily_search]
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=f"You are a data extraction specialist. Research the query and return results as {output_format}. Be precise and structured.",
    )
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    msgs = result.get("messages", [])
    for msg in reversed(msgs):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "{}"
