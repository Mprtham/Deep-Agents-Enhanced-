"""Basic smoke tests — no API calls, no LLM invocations."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_config_imports():
    import config
    assert config.APP_TITLE == "Deep Agents — Enhanced"
    assert config.WATERMARK_TEXT == "Made by Prathamesh Mishra"
    assert len(config.AVAILABLE_MODELS) > 0


def test_step_renderer_empty():
    from components.step_renderer import render_steps, _safe_str
    assert _safe_str("hello") == "hello"
    assert _safe_str("x" * 1000) == "x" * 500 + "…"
    assert _safe_str({"key": "val"}) is not None


def test_sidebar_logic():
    from components.sidebar import init_conversation_store, create_new_conversation, _format_time
    # Test _format_time doesn't crash on valid/invalid input
    assert isinstance(_format_time("2026-06-06T12:00:00"), str)
    assert isinstance(_format_time("bad-date"), str)
    # init_conversation_store and create_new_conversation require Streamlit runtime;
    # verify they are importable callables
    assert callable(init_conversation_store)
    assert callable(create_new_conversation)


def test_agent_core_imports():
    from agent_core import SYSTEM_PROMPT, extract_steps_from_events
    assert "Deep Agent" in SYSTEM_PROMPT
    steps = extract_steps_from_events([])
    assert steps == []


def test_css_file_exists():
    from pathlib import Path
    css = Path(__file__).parent.parent / "styles" / "main.css"
    assert css.exists()
    content = css.read_text()
    assert ".watermark" in content
    assert "#E84393" in content
    assert "Made by Prathamesh Mishra" not in content  # injected via Python, not CSS


def test_watermark_component():
    # Just import — actual rendering requires Streamlit runtime
    from components.watermark import inject_watermark
    assert callable(inject_watermark)
