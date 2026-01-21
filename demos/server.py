# add a new note
# delete a note
# retrieve a note based on the name
# list all the notes 

# resource - one particular entry of the notes 
# prompt - template prompt for the llm to summarize a note 

import resource
from mcp.server.fastmcp import FastMCP
import json
from pathlib import Path

mcp = FastMCP(name="Notes MCP Server")

NOTES_FILE = Path.home() / "my_notes.json"

# create a file (called my_notes.json) that contains a bunch of keys that will correspond to my notes
def load_notes() -> dict:
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text())
    return {}

def save_notes(notes):
    NOTES_FILE.write_text(json.dumps(notes, indent=2))

@mcp.tool()
def add_note(name: str, content: str) -> str:
    notes = load_notes() 
    notes[name] = content
    save_notes(notes)
    return f"Note '{name}' was added successfully."

@mcp.tool()
def delete_note(name: str) -> str:
    notes = load_notes()
    if name in notes:
        del notes[name]
        save_notes(notes)
        return f"Note '{name}' was deleted successfully."
    return f"Note '{name}' was not found."

@mcp.tool()
def get_note(name: str) -> str:
    notes = load_notes()
    if name in notes:
        return notes[name]
    return f"Note '{name}' was not found." 

@mcp.tool()
def list_notes() -> str:
    notes = load_notes()
    if not notes:
        return "No notes were found"
    return f"Notes: {', '.join(notes.keys())}" 

@mcp.resource("resource://{name}")
def get_note_resource(name: str) -> str:
    notes = load_notes()
    if name in notes:
        return notes[name]
    return f"Note '{name}' was not found." 

@mcp.resource("resource://reference")
def reference_resource() -> str:
    return "In order to save a note, simply add a 'name' for the entry and 'contents' for the entry's value."

@mcp.prompt()
def summarize_notes(name: str) -> str:
    notes = load_notes()
    if name in notes:
        return f"Here is a note: '{notes[name]}'. Please summarize it in a concise manner. Keep the summary to 100 words or less."
    return f"Note '{name}' was not found." 

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

