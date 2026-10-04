import uuid
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import get_agent
from db import (
    create_update_convo,
    delete_conversation,
    get_chat_history,
    init_db,
    list_conversations,
    save_chat_message,
)
from rag import add_document_to_vector_store
from tools import set_current_thid


app = FastAPI(title="HelloGPT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).parent / "frontend" / "dist"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    thread_id: str
    message: str = Field(min_length=1, max_length=20_000)
    model: str = "gemini-3.1-flash-lite"


def message_content(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/conversations")
def conversations() -> list[dict[str, str]]:
    return [
        {
            "thread_id": conversation.thread_id,
            "name": conversation.name,
            "updated_at": conversation.updated_at,
        }
        for conversation in list_conversations()
    ]


@app.post("/api/conversations")
def new_conversation() -> dict[str, str]:
    thread_id = str(uuid.uuid4())
    create_update_convo(thread_id, "", "New conversation")
    return {"thread_id": thread_id, "name": "New conversation"}


@app.get("/api/conversations/{thread_id}/messages")
def history(thread_id: str) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": message.content}
        for message in get_chat_history(thread_id)
    ]


@app.delete("/api/conversations/{thread_id}")
def remove_conversation(thread_id: str) -> dict[str, bool]:
    if not delete_conversation(thread_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    create_update_convo(request.thread_id, request.message, request.message[:48])
    set_current_thid(request.thread_id)
    save_chat_message(request.thread_id, "user", request.message)

    try:
        agent = get_agent(request.model)
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config={"configurable": {"thread_id": request.thread_id}},
        )
        assistant_message = result["messages"][-1]
        answer = message_content(assistant_message)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Unable to generate a response: {exc}") from exc

    save_chat_message(request.thread_id, "assistant", answer)
    return {"role": "assistant", "content": answer}


@app.post("/api/conversations/{thread_id}/files")
async def upload_file(thread_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Upload a PDF, DOCX, TXT, or MD file.")
    destination = UPLOAD_DIR / f"{uuid.uuid4()}{suffix}"
    destination.write_bytes(await file.read())
    try:
        result = add_document_to_vector_store(str(destination), thread_id)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Unable to index file: {exc}") from exc
    return result


if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        requested = FRONTEND / path
        return FileResponse(requested if requested.is_file() else FRONTEND / "index.html")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
