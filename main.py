"""
CLI entry point — runs the agent interactively in the terminal.
For the full UI, use: streamlit run streamlit_app.py
"""

import os
import uuid
from dotenv import load_dotenv

load_dotenv()


def main():
    print("=" * 60)
    print("  Deep Agents — Enhanced CLI")
    print("  Made by Prathamesh Mishra")
    print("=" * 60)
    print()

    model_id = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")
    print(f"Using model: {model_id}")
    print("Type 'quit' to exit, 'new' to start a new thread.")
    print()

    from agent_core import build_agent, run_agent_response

    agent = build_agent(model_id, backend="memory")
    thread_id = str(uuid.uuid4())
    history: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "new":
            thread_id = str(uuid.uuid4())
            history = []
            print("[New conversation started]")
            continue

        try:
            response, steps = run_agent_response(agent, user_input, thread_id, history)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

            print(f"\nAgent: {response}")
            if steps:
                print(f"\n[Used {len(steps)} tool(s) internally]")
            print()
        except Exception as e:
            print(f"\n[Error] {e}\n")


if __name__ == "__main__":
    main()
