import streamlit as st
from datetime import datetime


def render_user_message(content: str, timestamp: str = "") -> None:
    ts = timestamp or datetime.now().strftime("%H:%M")
    st.markdown(
        f"""
        <div class="user-message-container">
            <div>
                <div class="user-message-bubble">{content}</div>
                <div class="user-message-time">{ts}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_agent_message_start() -> None:
    st.markdown(
        """
        <div class="agent-message-container">
            <div class="agent-avatar">🧠</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_thinking_indicator() -> None:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:12px; margin: 8px 0;">
            <div class="agent-avatar" style="width:36px;height:36px;border-radius:50%;
                background:linear-gradient(135deg,#2C3E8C,#E84393);display:flex;
                align-items:center;justify-content:center;font-size:18px;">🧠</div>
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


def render_error_card(title: str, message: str, hint: str = "") -> None:
    hint_html = f"<div style='margin-top:8px;font-size:12px;color:#718096;'>{hint}</div>" if hint else ""
    st.markdown(
        f"""
        <div class="error-card">
            <div class="error-card-title">⚠️ {title}</div>
            <div class="error-card-message">{message}</div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_screen() -> None:
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-icon">🧠</div>
            <div class="welcome-title">Deep Agents — Enhanced</div>
            <div class="welcome-subtitle">
                An AI assistant that thinks, plans, searches the web,<br>
                and coordinates specialist sub-agents to solve complex tasks.
            </div>
            <div class="capability-chips">
                <div class="capability-chip">🔎 Live web search</div>
                <div class="capability-chip">📋 Step-by-step planning</div>
                <div class="capability-chip">🤖 Sub-agent delegation</div>
                <div class="capability-chip">📁 File read &amp; write</div>
                <div class="capability-chip">💬 Conversation memory</div>
                <div class="capability-chip">⚡ Streaming responses</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
