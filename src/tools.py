from pathlib import Path

import vector_index

KNOWLEDGE_DIR = Path("knowledge")

# JSON schemas sent to Ollama so the model knows what tools exist and how to call them.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": "List all documents available in the knowledge base.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a document from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename to read, e.g. 'design_patterns.md'",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Semantically search the knowledge base for sections relevant to a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language question or topic to search for",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write content to a file in the knowledge base. "
                "Use only when explicitly asked to save or update notes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename to write, e.g. 'new_topic.md'",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full Markdown content to write",
                    },
                },
                "required": ["filename", "content"],
            },
        },
    },
]


def list_documents() -> str:
    files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not files:
        return "No documents found in the knowledge base."
    return "\n".join(f.name for f in files)


def read_file(filename: str) -> str:
    path = KNOWLEDGE_DIR / filename
    if not path.exists():
        return f"Error: '{filename}' not found in the knowledge base."
    return path.read_text(encoding="utf-8")


def search_notes_tool(query: str) -> str:
    matches = vector_index.semantic_search(query)
    if not matches:
        return "No relevant sections found for that query."
    return vector_index.build_context(matches)


def write_file(filename: str, content: str) -> str:
    path = KNOWLEDGE_DIR / filename
    path.write_text(content, encoding="utf-8")
    # Keep the vector index in sync so new notes are immediately searchable.
    vector_index.build_index()
    return f"'{filename}' saved to the knowledge base and indexed."


def execute(name: str, args: dict) -> str:
    if name == "list_documents":
        return list_documents()
    if name == "read_file":
        return read_file(args.get("filename", ""))
    if name == "search_notes":
        return search_notes_tool(args.get("query", ""))
    if name == "write_file":
        return write_file(args.get("filename", ""), args.get("content", ""))
    return f"Unknown tool: '{name}'"