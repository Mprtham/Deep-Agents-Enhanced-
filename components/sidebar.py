import streamlit as st
from datetime import datetime
import uuid


def init_conversation_store():
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None


def create_new_conversation():
    conv_id = str(uuid.uuid4())
    st.session_state.conversations[conv_id] = {
        "id": conv_id,
        "title": "New conversation",
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    st.session_state.active_conversation_id = conv_id
    if "messages" in st.session_state:
        st.session_state.messages = []
    return conv_id


def get_active_conversation():
    cid = st.session_state.get("active_conversation_id")
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]
    return None


def update_active_conversation_title(title: str):
    cid = st.session_state.get("active_conversation_id")
    if cid and cid in st.session_state.conversations:
        st.session_state.conversations[cid]["title"] = title[:50]
        st.session_state.conversations[cid]["updated_at"] = datetime.now().isoformat()


def sync_messages_to_conversation():
    cid = st.session_state.get("active_conversation_id")
    if cid and cid in st.session_state.conversations:
        st.session_state.conversations[cid]["messages"] = st.session_state.get(
            "messages", []
        )
        st.session_state.conversations[cid]["updated_at"] = datetime.now().isoformat()


def _format_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now()
        diff = now - dt
        if diff.total_seconds() < 60:
            return "just now"
        if diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        if diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        return dt.strftime("%b %d")
    except Exception:
        return ""


def render_sidebar():
    init_conversation_store()

    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 20px 0 12px; border-bottom: 1px solid rgba(44,62,140,0.4); margin-bottom: 8px;">
                <div style="font-size:13px; font-weight:600; color:#718096; letter-spacing:0.08em;
                            text-transform:uppercase; margin-bottom:12px;">Conversations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("＋  New Chat", use_container_width=True, key="new_chat_btn"):
            create_new_conversation()
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        convs = sorted(
            st.session_state.conversations.values(),
            key=lambda c: c.get("updated_at", ""),
            reverse=True,
        )

        for conv in convs:
            cid = conv["id"]
            is_active = cid == st.session_state.get("active_conversation_id")
            title = conv.get("title", "Untitled")
            time_str = _format_time(conv.get("updated_at", ""))
            msg_count = len(conv.get("messages", []))

            border_style = (
                "border: 1px solid rgba(44,62,140,0.6); background: rgba(44,62,140,0.12);"
                if is_active
                else "border: 1px solid transparent;"
            )

            col1, col2 = st.columns([5, 1])
            with col1:
                label = f"{'● ' if is_active else ''}{title}"
                if st.button(
                    label,
                    key=f"conv_{cid}",
                    use_container_width=True,
                    help=f"{msg_count} messages · {time_str}",
                ):
                    sync_messages_to_conversation()
                    st.session_state.active_conversation_id = cid
                    st.session_state.messages = conv.get("messages", [])
                    st.rerun()

            with col2:
                if st.button("✕", key=f"del_{cid}", help="Delete"):
                    del st.session_state.conversations[cid]
                    if st.session_state.active_conversation_id == cid:
                        st.session_state.active_conversation_id = None
                        st.session_state.messages = []
                    st.rerun()

        if not convs:
            st.markdown(
                "<div style='color:#4A5568; font-size:13px; text-align:center; padding:20px;'>"
                "No conversations yet.<br>Start by clicking New Chat.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            "<div style='font-size:11px; color:#4A5568; text-align:center;'>Deep Agents v1.0</div>",
            unsafe_allow_html=True,
        )
