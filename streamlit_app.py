"""
Deep Agents — Enhanced Edition
Built by Prathamesh Mishra
"""

from __future__ import annotations

import os
import uuid
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Deep Agents — Enhanced",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "main.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Components ────────────────────────────────────────────────────────────────
from components.watermark import inject_watermark
from components.sidebar import (
    render_sidebar,
    init_conversation_store,
    create_new_conversation,
    get_active_conversation,
    update_active_conversation_title,
    sync_messages_to_conversation,
)
from components.step_renderer import render_steps
from components.chat_message import (
    render_thinking_indicator,
    render_error_card,
    render_welcome_screen,
)
from config import AVAILABLE_MODELS, DEFAULT_MODEL, APP_TITLE

# ── Watermark (always first) ──────────────────────────────────────────────────
inject_watermark()

# ── Session state bootstrap ───────────────────────────────────────────────────
init_conversation_store()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL

if "backend" not in st.session_state:
    st.session_state.backend = "memory"

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "agent" not in st.session_state:
    st.session_state.agent = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar()


# ── API key validation helper ─────────────────────────────────────────────────
def check_api_keys() -> list[str]:
    missing = []
    model = st.session_state.selected_model
    provider = model.split(":")[0] if ":" in model else "openai"
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if provider == "groq" and not os.getenv("GROQ_API_KEY"):
        missing.append("GROQ_API_KEY")
    return missing


# ── Agent builder (cached in session) ────────────────────────────────────────
def get_or_build_agent():
    key = f"{st.session_state.selected_model}:{st.session_state.backend}"
    if st.session_state.get("_agent_key") != key or st.session_state.agent is None:
        from agent_core import build_agent
        try:
            st.session_state.agent = build_agent(
                st.session_state.selected_model,
                st.session_state.backend,
            )
            st.session_state._agent_key = key
        except Exception as e:
            st.session_state.agent = None
            return None, str(e)
    return st.session_state.agent, None


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div class="app-icon">🧠</div>
        <div>
            <div class="app-title">Deep Agents — Enhanced</div>
            <div class="app-subtitle">Multi-step reasoning · Web search · Sub-agent delegation</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Model selector ────────────────────────────────────────────────────────────
with st.container():
    col_label, *model_cols, col_backend = st.columns(
        [1.5] + [1.2] * len(AVAILABLE_MODELS) + [2]
    )
    col_label.markdown(
        "<div style='padding-top:8px;font-size:13px;color:#718096;font-weight:600;'>Model</div>",
        unsafe_allow_html=True,
    )
    for i, model_info in enumerate(AVAILABLE_MODELS):
        with model_cols[i]:
            is_active = st.session_state.selected_model == model_info["id"]
            btn_style = (
                "background:linear-gradient(135deg,#2C3E8C,#3D52B5);color:white;border:none;"
                if is_active
                else "background:#1A1A2E;color:#718096;border:1px solid rgba(44,62,140,0.4);"
            )
            if st.button(
                model_info["label"],
                key=f"model_{model_info['id']}",
                use_container_width=True,
                help=model_info["id"],
            ):
                if st.session_state.selected_model != model_info["id"]:
                    st.session_state.selected_model = model_info["id"]
                    st.session_state.agent = None
                    st.rerun()

    with col_backend:
        backend_opts = {"memory": "🧠 In-Memory", "filesystem": "💾 Filesystem", "store": "🔗 Cross-Session"}
        new_backend = st.selectbox(
            "Backend",
            options=list(backend_opts.keys()),
            format_func=lambda x: backend_opts[x],
            index=list(backend_opts.keys()).index(st.session_state.backend),
            label_visibility="collapsed",
        )
        if new_backend != st.session_state.backend:
            st.session_state.backend = new_backend
            st.session_state.agent = None
            st.rerun()

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── API key warning ───────────────────────────────────────────────────────────
missing_keys = check_api_keys()
if missing_keys:
    st.warning(
        f"⚠️ Missing API key(s): **{', '.join(missing_keys)}**. "
        "Add them to your `.env` file or set them as environment variables.",
        icon="🔑",
    )

# ── Ensure there's an active conversation ────────────────────────────────────
if st.session_state.active_conversation_id is None:
    create_new_conversation()

# ── Render existing messages ──────────────────────────────────────────────────
if not st.session_state.messages:
    render_welcome_screen()
else:
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        steps = msg.get("steps", [])

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(content)
                if steps:
                    render_steps(steps)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything — I can research, plan, write code, and more…"):
    if missing_keys:
        render_error_card(
            "API Key Required",
            f"Please configure: {', '.join(missing_keys)}",
            "Add keys to your .env file and restart the app.",
        )
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Update conversation title from first message
    if len(st.session_state.messages) == 1:
        update_active_conversation_title(prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Build agent
    agent, build_error = get_or_build_agent()
    if build_error or agent is None:
        render_error_card(
            "Agent Initialisation Failed",
            build_error or "Unknown error building the agent.",
            "Check your API keys and model selection.",
        )
        st.stop()

    # Stream response
    with st.chat_message("assistant", avatar="🧠"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            """
            <div style="display:flex;align-items:center;gap:12px;padding:4px 0;">
                <div class="thinking-indicator">
                    <span>Thinking</span>
                    <div class="thinking-dots">
                        <div class="thinking-dot"></div>
                        <div class="thinking-dot"></div>
                        <div class="thinking-dot"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        response_text = ""
        accumulated_steps: list[dict] = []
        stream_placeholder = st.empty()
        error_occurred = False

        try:
            from agent_core import stream_agent_response

            history = st.session_state.messages[:-1]
            last_content = ""

            for chunk_content, steps_so_far in stream_agent_response(
                agent,
                prompt,
                st.session_state.thread_id,
                history,
            ):
                if chunk_content != last_content:
                    thinking_placeholder.empty()
                    response_text = chunk_content
                    stream_placeholder.markdown(response_text)
                    last_content = chunk_content
                accumulated_steps = steps_so_far

            if not response_text:
                # Fallback to non-streaming
                thinking_placeholder.empty()
                from agent_core import run_agent_response
                response_text, accumulated_steps = run_agent_response(
                    agent, prompt, st.session_state.thread_id, history
                )
                stream_placeholder.markdown(response_text)

        except Exception as e:
            thinking_placeholder.empty()
            stream_placeholder.empty()
            error_occurred = True
            err_msg = str(e)
            if "api_key" in err_msg.lower() or "authentication" in err_msg.lower():
                render_error_card(
                    "Authentication Error",
                    "Invalid or missing API key.",
                    "Check your OPENAI_API_KEY or GROQ_API_KEY in .env",
                )
            elif "rate_limit" in err_msg.lower() or "429" in err_msg:
                render_error_card(
                    "Rate Limit",
                    "Too many requests. Please wait a moment and try again.",
                )
            elif "model" in err_msg.lower() and "not found" in err_msg.lower():
                render_error_card(
                    "Model Not Found",
                    f"The selected model may not be available: {st.session_state.selected_model}",
                    "Try switching to a different model.",
                )
            else:
                render_error_card("Something went wrong", err_msg[:300])

        if not error_occurred and response_text:
            thinking_placeholder.empty()
            if accumulated_steps:
                render_steps(accumulated_steps)

            # Save to session
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "steps": accumulated_steps,
            })
            sync_messages_to_conversation()
