#!/usr/bin/env python3
"""
mem0 Memory Retrieve Hook for Cursor
Searches mem0 for relevant memories before each prompt and injects them into context.
Also auto-saves each prompt to mem0 for continuous learning.

Environment Variables:
  MEM0_API_KEY: Required - Your mem0 API key from https://app.mem0.ai
  MEM0_USER_ID: Optional - User identifier for memory scoping (default: cursor-user)
  MEM0_TOP_K: Optional - Number of memories to retrieve (default: 5)
  MEM0_THRESHOLD: Optional - Minimum similarity score (default: 0.3)
  MEM0_AUTO_SAVE: Optional - Auto-save prompts to memory (default: true)
"""

import json
import os
import sys
import threading
from pathlib import Path


def load_env_file():
    """Load .env file from workspace if it exists."""
    # Try workspace roots from Cursor input
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

    # Also try current directory
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
        "top_k": int(os.environ.get("MEM0_TOP_K", "5")),
        "threshold": float(os.environ.get("MEM0_THRESHOLD", "0.3")),
        "auto_save": os.environ.get("MEM0_AUTO_SAVE", "true").lower() == "true",
    }


def search_memories(query: str, config: dict) -> list:
    """Search mem0 for relevant memories."""
    try:
        from mem0 import MemoryClient

        client = MemoryClient(api_key=config["api_key"])
        response = client.search(
            query=query,
            filters={"user_id": config["user_id"]},
            top_k=config["top_k"],
            threshold=config["threshold"]
        )
        if isinstance(response, dict):
            return response.get("results", [])
        return response if isinstance(response, list) else []
    except ImportError:
        return []
    except Exception:
        return []


def save_prompt_async(prompt: str, config: dict):
    """Save user prompt to mem0 in background thread."""
    def _save():
        try:
            from mem0 import MemoryClient
            client = MemoryClient(api_key=config["api_key"])
            client.add(
                messages=[{"role": "user", "content": prompt}],
                user_id=config["user_id"]
            )
        except Exception:
            pass

    thread = threading.Thread(target=_save)
    thread.start()
    thread.join(timeout=2.0)


def format_memories(results: list) -> str:
    """Format memories for context injection."""
    memories = []
    for r in results:
        memory = r.get("memory", "")
        if memory:
            categories = r.get("categories", [])
            if categories:
                memories.append(f"- [{', '.join(categories)}] {memory}")
            else:
                memories.append(f"- {memory}")

    if not memories:
        return ""

    return "## Relevant memories from previous conversations:\n" + "\n".join(memories)


def main():
    load_env_file()

    # Read hook input from stdin (Cursor format)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # No blocking, just exit
        print(json.dumps({"action": "continue"}))
        sys.exit(0)

    # Get prompt from Cursor's input schema
    user_prompt = input_data.get("prompt", "") or input_data.get("query", "")
    if not user_prompt:
        print(json.dumps({"action": "continue"}))
        sys.exit(0)

    config = get_config()

    if not config["api_key"]:
        print(json.dumps({"action": "continue"}))
        sys.exit(0)

    # Search for relevant memories
    results = search_memories(user_prompt, config)

    # Auto-save this prompt
    if config["auto_save"]:
        save_prompt_async(user_prompt, config)

    # Output memories as context modification
    if results:
        message = format_memories(results)
        if message:
            # Cursor expects JSON output with modifications
            print(json.dumps({
                "action": "continue",
                "context": message
            }))
            sys.exit(0)

    print(json.dumps({"action": "continue"}))


if __name__ == "__main__":
    main()
