import streamlit as st
import json
from typing import Any


def _safe_str(val: Any, max_len: int = 500) -> str:
    if isinstance(val, str):
        return val[:max_len] + ("…" if len(val) > max_len else "")
    try:
        return json.dumps(val, indent=2)[:max_len]
    except Exception:
        return str(val)[:max_len]


def render_steps(steps: list[dict]) -> None:
    if not steps:
        return

    planning_steps = [s for s in steps if s.get("type") == "plan"]
    search_steps = [s for s in steps if s.get("type") == "search"]
    subagent_steps = [s for s in steps if s.get("type") == "subagent"]
    file_steps = [s for s in steps if s.get("type") in ("file_read", "file_write")]
    tool_steps = [
        s
        for s in steps
        if s.get("type") not in ("plan", "search", "subagent", "file_read", "file_write")
    ]

    if planning_steps:
        with st.expander("📋 Agent Plan", expanded=False):
            for i, step in enumerate(planning_steps, 1):
                content = step.get("content", step.get("output", ""))
                st.markdown(
                    f"<div class='step-card'>"
                    f"<div class='step-card-header'>Step {i}</div>"
                    f"<div class='step-card-content'>{_safe_str(content)}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    if search_steps:
        with st.expander(f"🔎 Web Searches ({len(search_steps)})", expanded=False):
            for step in search_steps:
                query = step.get("query", step.get("input", ""))
                result = step.get("result", step.get("output", ""))
                st.markdown(
                    f"<div class='step-card'>"
                    f"<div class='step-card-header'>🔍 {_safe_str(query, 120)}</div>"
                    f"<div class='step-card-content'>{_safe_str(result, 300)}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    if subagent_steps:
        with st.expander(f"🤖 Sub-Agent Tasks ({len(subagent_steps)})", expanded=False):
            for step in subagent_steps:
                name = step.get("agent", step.get("name", "Sub-agent"))
                task = step.get("task", step.get("input", ""))
                result = step.get("result", step.get("output", ""))
                st.markdown(
                    f"<div class='step-card'>"
                    f"<div class='step-card-header'>🤖 {name}</div>"
                    f"<div class='step-card-content'><b>Task:</b> {_safe_str(task, 200)}<br>"
                    f"<b>Result:</b> {_safe_str(result, 300)}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    if file_steps:
        with st.expander(f"📁 File Operations ({len(file_steps)})", expanded=False):
            for step in file_steps:
                op = "Read" if step.get("type") == "file_read" else "Write"
                path = step.get("path", step.get("file", ""))
                content = step.get("content", step.get("output", ""))
                icon = "📖" if op == "Read" else "✏️"
                st.markdown(
                    f"<div class='step-card'>"
                    f"<div class='step-card-header'>{icon} {op}: {_safe_str(path, 80)}</div>"
                    f"<div class='step-card-content'>{_safe_str(content, 400)}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    if tool_steps:
        with st.expander(f"⚙️ Tool Calls ({len(tool_steps)})", expanded=False):
            for step in tool_steps:
                tool_name = step.get("tool", step.get("type", "tool"))
                inp = step.get("input", step.get("args", ""))
                out = step.get("output", step.get("result", ""))
                st.markdown(
                    f"<div class='step-card'>"
                    f"<div class='step-card-header'>⚙️ {tool_name}</div>"
                    f"<div class='step-card-content'>"
                    f"<b>Input:</b> {_safe_str(inp, 200)}<br>"
                    f"<b>Output:</b> {_safe_str(out, 300)}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


def render_tool_call_stream(tool_name: str, tool_input: str, tool_output: str = "") -> None:
    icon_map = {
        "tavily_search": "🔎",
        "search": "🔎",
        "read_file": "📖",
        "write_file": "✏️",
        "plan": "📋",
        "subagent": "🤖",
    }
    icon = icon_map.get(tool_name.lower(), "⚙️")
    with st.expander(f"{icon} {tool_name}", expanded=False):
        if tool_input:
            st.markdown(f"**Input:** `{_safe_str(tool_input, 300)}`")
        if tool_output:
            st.markdown(f"**Output:** {_safe_str(tool_output, 500)}")
