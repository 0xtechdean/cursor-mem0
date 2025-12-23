#!/usr/bin/env python3
"""
Tests for mem0 Cursor hooks
Run with: python -m pytest tests/ -v
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add hooks directory to path
HOOKS_DIR = Path(__file__).parent.parent / ".cursor" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))


class TestMemoryRetrieveHook:
    """Tests for memory_retrieve.py hook"""

    def test_returns_continue_without_api_key(self):
        """Should return continue action when no API key configured"""
        input_data = json.dumps({"prompt": "test prompt"})

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_retrieve.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    def test_returns_continue_without_prompt(self):
        """Should return continue action when no prompt provided"""
        input_data = json.dumps({})

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_retrieve.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    def test_handles_invalid_json(self):
        """Should handle invalid JSON input gracefully"""
        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_retrieve.py")],
            input="not valid json",
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    @pytest.mark.skipif(
        not os.environ.get("MEM0_API_KEY"),
        reason="MEM0_API_KEY not set"
    )
    def test_retrieves_memories_with_valid_key(self):
        """Should retrieve memories when API key is valid"""
        input_data = json.dumps({"prompt": "test query"})

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_retrieve.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env=os.environ
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"
        # May or may not have context depending on stored memories


class TestMemorySaveHook:
    """Tests for memory_save.py hook"""

    def test_returns_continue_without_api_key(self):
        """Should return continue action when no API key configured"""
        input_data = json.dumps({
            "transcript": [
                {"role": "user", "content": "test message"}
            ]
        })

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_save.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    def test_returns_continue_without_transcript(self):
        """Should return continue action when no transcript provided"""
        input_data = json.dumps({})

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_save.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    def test_handles_invalid_json(self):
        """Should handle invalid JSON input gracefully"""
        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_save.py")],
            input="not valid json",
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    def test_handles_messages_field(self):
        """Should handle 'messages' field as alternative to 'transcript'"""
        input_data = json.dumps({
            "messages": [
                {"role": "user", "content": "test message"}
            ]
        })

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_save.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env={**os.environ, "MEM0_API_KEY": ""}
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"

    @pytest.mark.skipif(
        not os.environ.get("MEM0_API_KEY"),
        reason="MEM0_API_KEY not set"
    )
    def test_saves_memories_with_valid_key(self):
        """Should save memories when API key is valid"""
        input_data = json.dumps({
            "transcript": [
                {"role": "user", "content": "Test save from pytest"}
            ]
        })

        result = subprocess.run(
            ["python3", str(HOOKS_DIR / "memory_save.py")],
            input=input_data,
            capture_output=True,
            text=True,
            env=os.environ
        )

        output = json.loads(result.stdout)
        assert output["action"] == "continue"


class TestConfigLoading:
    """Tests for configuration loading"""

    def test_default_user_id(self):
        """Should use default user ID when not specified"""
        from memory_retrieve import get_config

        with patch.dict(os.environ, {"MEM0_API_KEY": "test", "MEM0_USER_ID": ""}, clear=False):
            # Remove MEM0_USER_ID if it exists
            os.environ.pop("MEM0_USER_ID", None)
            config = get_config()
            assert config["user_id"] == "cursor-user"

    def test_custom_user_id(self):
        """Should use custom user ID when specified"""
        from memory_retrieve import get_config

        with patch.dict(os.environ, {"MEM0_USER_ID": "custom-user"}, clear=False):
            config = get_config()
            assert config["user_id"] == "custom-user"

    def test_auto_save_default_true(self):
        """Should default auto_save to true"""
        from memory_retrieve import get_config

        with patch.dict(os.environ, {"MEM0_AUTO_SAVE": ""}, clear=False):
            os.environ.pop("MEM0_AUTO_SAVE", None)
            config = get_config()
            assert config["auto_save"] == True

    def test_auto_save_false(self):
        """Should respect MEM0_AUTO_SAVE=false"""
        from memory_retrieve import get_config

        with patch.dict(os.environ, {"MEM0_AUTO_SAVE": "false"}, clear=False):
            config = get_config()
            assert config["auto_save"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
