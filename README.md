# mem0 Plugin for Cursor

Persistent memory for Cursor using [mem0.ai](https://mem0.ai) - remembers context across conversations.

## Features

- **Auto-Save Every Prompt**: Each prompt is automatically saved to mem0
- **Automatic Memory Retrieval**: Relevant memories are injected before each prompt
- **Conversation Storage**: Full conversations saved when sessions end
- **Semantic Search**: Vector-based search for intelligent memory retrieval

## Installation

### 1. Copy hooks to your project

```bash
cp -r .cursor /path/to/your/project/
```

Or for global installation:
```bash
cp -r .cursor ~/.cursor/
```

### 2. Install dependency

```bash
pip install mem0ai
```

### 3. Configure environment

Create a `.env` file in your project:

```bash
MEM0_API_KEY=your-api-key-here
MEM0_USER_ID=cursor-user

# Optional
MEM0_TOP_K=5
MEM0_THRESHOLD=0.3
MEM0_AUTO_SAVE=true
```

Get your API key from [app.mem0.ai](https://app.mem0.ai)

### 4. Restart Cursor

The hooks will be active after restart.

## Structure

```
.cursor/
├── hooks.json           # Hook configuration
└── hooks/
    ├── memory_retrieve.py   # Memory retrieval + auto-save
    └── memory_save.py       # Session-end save
```

## How It Works

### beforeSubmitPrompt Hook

1. Searches mem0 for relevant memories
2. Injects them as context
3. Auto-saves the prompt to mem0

### stop Hook

1. Extracts recent messages from conversation
2. Saves them to mem0 for future retrieval

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM0_API_KEY` | Your mem0 API key (required) | - |
| `MEM0_USER_ID` | User identifier | `cursor-user` |
| `MEM0_TOP_K` | Memories to retrieve | `5` |
| `MEM0_THRESHOLD` | Similarity threshold | `0.3` |
| `MEM0_AUTO_SAVE` | Auto-save prompts | `true` |
| `MEM0_SAVE_MESSAGES` | Messages to save on stop | `10` |

## Testing

Run the test suite:

```bash
pip install pytest
python -m pytest tests/ -v
```

## License

MIT

## Also Available

- [Claude Code version](https://github.com/0xtechdean/claude-code-mem0)
