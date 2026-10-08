# HelloGPT

> **Work in progress**
>
> HelloGPT is a ChatGPT-style assistant with a React + TypeScript frontend and a
> Python/FastAPI backend. It supports authenticated workspaces, persistent
> conversations, Gemini-powered chat, web search tools, and document-grounded
> answers. The project is still evolving, so APIs, UI, and configuration may
> change.

## Overview

HelloGPT is being developed as a practical AI assistant with:

- A dark, responsive chat interface inspired by modern AI products
- Conversation history backed by SQLite
- LangGraph-based agent orchestration
- Google Gemini model integration
- Long-term memory tools
- Web search tooling
- Retrieval-augmented generation for uploaded documents
- PDF, DOCX, TXT, and Markdown document ingestion
- A FastAPI API that serves the frontend in production

## Current status

### Currently available

- Create and select conversations
- Persist user and assistant messages
- Send chat messages through the FastAPI backend
- Choose between the configured Gemini model names from the frontend
- Upload supported documents for indexing
- Responsive sidebar with conversation history
- Production frontend build through Vite

### Still in progress

- Production database and deployment configuration
- Streaming assistant responses
- Conversation renaming and search behavior
- Complete document-management UI
- Automated backend and frontend test coverage
- Production-grade observability and error reporting
- Final security, privacy, and rate-limit review

## Technology stack

### Frontend

- React 18
- TypeScript
- Vite
- `lucide-react`
- CSS-based responsive styling and animations

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- LangChain
- LangGraph
- SQLAlchemy
- SQLite for local persistence and LangGraph checkpoints
- Chroma for vector search
- Google Gemini for model and embedding access

## Project structure

```text
.
├── app.py                    # FastAPI application and API routes
├── agent.py                  # LangGraph agent construction and model selection
├── db.py                     # SQLAlchemy models and conversation persistence
├── rag.py                    # Document parsing, chunking, and vector indexing
├── tools.py                  # Agent tools such as memory and web search
├── requirements.txt          # Python dependencies
├── data/                     # Local SQLite and LangGraph checkpoint files
├── chroma_db/                # Local Chroma vector-store data
├── uploads/                  # Temporary uploaded document files
└── frontend/
    ├── src/
    │   ├── App.tsx           # Main chat interface and API integration
    │   ├── main.tsx          # React entry point
    │   └── styles.css        # Application styling
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- A Google Gemini API key
- A Tavily API key for the web-search tool

## Local setup

The commands below are written for PowerShell on Windows.

### 1. Clone the project

```powershell
git clone <repository-url>
Set-Location .\RAGRAPH_bot
```

### 2. Create and activate a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
JWT_SECRET_KEY=replace-with-a-long-random-secret
```

`GEMINI_API_KEY` is used for chat and document embeddings. `TAVILY_API_KEY`
is used by the web-search tool. Set `JWT_SECRET_KEY` to a long, random value
before sharing or deploying the application; the built-in fallback is intended
only for local development.

Do not commit `.env` or any API keys to source control.

### 5. Install frontend dependencies

```powershell
Set-Location .\frontend
npm install
Set-Location ..
```

### 6. Start the development servers

Start the backend in one terminal:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Start the Vite frontend in a second terminal:

```powershell
Set-Location .\frontend
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The Vite development server proxies `/api` requests to the FastAPI server at `http://127.0.0.1:8000`.

Create an account from the login page before using the chat workspace. Access
tokens expire after 30 minutes and are sent as Bearer tokens by the frontend.

## Production frontend build

Build the frontend:

```powershell
Set-Location .\frontend
npm run build
```

The generated files are placed in `frontend/dist`. When that directory exists, FastAPI serves the built frontend and its assets.

Run the backend:

```powershell
Set-Location ..
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Check backend availability |
| `POST` | `/api/auth/register` | Create a user account |
| `POST` | `/api/auth/token` | Log in and receive a Bearer token |
| `GET` | `/api/auth/me` | Return the authenticated user |
| `GET` | `/api/conversations` | List saved conversations |
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations/{thread_id}/messages` | Load conversation history |
| `DELETE` | `/api/conversations/{thread_id}` | Delete a conversation |
| `POST` | `/api/chat` | Send a message and receive an assistant response |
| `POST` | `/api/conversations/{thread_id}/files` | Upload and index a supported document |

All conversation, chat, and upload endpoints require an
`Authorization: Bearer <token>` header. Registration and token requests do not
require authentication.

Example chat request:

```json
{
  "thread_id": "conversation-id",
  "message": "Explain retrieval-augmented generation.",
  "model": "gemini-3.1-flash-lite"
}
```

The backend accepts these model names: `gemini-3.8`, `gemini-3.5`,
`gemini-2.5-flash`, and `gemini-3.1-flash-lite`. The frontend currently
switches between `gemini-3.1-flash-lite` and `gemini-2.5-flash`.

### Document uploads

Uploads are limited to PDF, DOCX, TXT, and Markdown files smaller than 10 MB.
Files are parsed, split into chunks, and stored in the local Chroma database
with the conversation thread ID as metadata. The original uploaded file is
removed after indexing.

## Development notes

- Local database files and vector-store data are created at runtime.
- The frontend currently uses a non-streaming chat request and displays a loading state while waiting for the response.
- Model names are validated by the agent layer; keep frontend model options aligned with `agent.py`.
- Uploaded documents are associated with a conversation thread for retrieval.
- The project currently favors local development and experimentation over deployment hardening.
- The local application stores users, conversations, messages, and memories in
  `data/memory.db`; LangGraph checkpoints are stored in `data/langgraph_checkpoint.dqlite`.
- Do not use the development JWT secret or SQLite/local vector storage as-is
  for a production deployment.

## Validation

Run the frontend type check and production build:

```powershell
Set-Location .\frontend
npm run build
```

Before making a production deployment, add and run backend tests, frontend
interaction tests, security checks, and a deployment-specific configuration
review.

## Contributing

This project is still being shaped. When contributing:

1. Keep changes focused and document behavior changes.
2. Avoid committing secrets, local databases, uploads, or generated build artifacts.
3. Run the frontend build before opening a pull request.
4. Describe known limitations and follow-up work clearly.

## License

No project license has been defined yet. Until a license is added, treat the repository as proprietary and obtain permission before redistributing or reusing the code.
