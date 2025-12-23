#!/usr/bin/env python3
"""
mem0 Memory Save Hook for Cursor
Stores conversation context to mem0 when a session ends.

Environment Variables:
  MEM0_API_KEY: Required - Your mem0 API key from https://app.mem0.ai
  MEM0_USER_ID: Optional - User identifier for memory scoping (default: cursor-user)
  MEM0_SAVE_MESSAGES: Optional - Number of recent messages to save (default: 10)
"""

import json
import os
import sys
from pathlib import Path


def load_env_file():
    """Load .env file from workspace if it exists."""
    try:
        input_data = json.loads(os.environ.get("CURSOR_HOOK_INPUT", "{}"))
        workspace_roots = input_data.get("workspace_roots", [])
        for root in workspace_roots:
            env_path = Path(root) / ".env"
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ.setdefault(key.strip(), value.strip())
                break
    except:
        pass

    env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def get_config():
    """Get configuration from environment variables."""
    return {
        "api_key": os.environ.get("MEM0_API_KEY", ""),
        "user_id": os.environ.get("MEM0_USER_ID", "cursor-user"),
        "save_messages": int(os.environ.get("MEM0_SAVE_MESSAGES", "10")),
    }


def extract_messages(input_data: dict, max_messages: int) -> list:
    """Extract recent messages from the session transcript."""
    # Cursor may use different field names
    transcript = input_data.get("transcript", []) or input_data.get("messages", [])

    if not transcript:
        return []

    recent = transcript[-max_messages:]

    messages = []
    for msg in recent:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
                elif isinstance(part, str):
                    text_parts.append(part)
            content = " ".join(text_parts)

        if role and content and isinstance(content, str):
            if len(content) > 2000:
                content = content[:2000] + "..."

            messages.append({
                "role": role,
                "content": content
            })

    return messages


def save_memories(messages: list, config: dict) -> bool:
    """Save messages to mem0."""
    try:
        from mem0 import MemoryClient

        client = MemoryClient(api_key=config["api_key"])
        client.add(messages, user_id=config["user_id"])
        return True
    except ImportError:
        return False
    except Exception:
        return False


def main():
    load_env_file()

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"action": "continue"}))
        sys.exit(0)

    config = get_config()

    if not config["api_key"]:
        print(json.dumps({"action": "continue"}))
        sys.exit(0)

    messages = extract_messages(input_data, config["save_messages"])

    if messages:
        save_memories(messages, config)

    print(json.dumps({"action": "continue"}))


if __name__ == "__main__":
    main()
