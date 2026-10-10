# Pagetrail

**Every answer leaves a trail back to a page.**

Pagetrail answers questions from your own documents, shows where each answer
came from, and says so when the answer isn't there. It also searches the web and
keeps a memory you can inspect.

> **Work in progress.** Core chat, accounts, document upload and retrieval work
> today. Page-level citations, streaming, automated tests and published
> evaluation results are in progress (see [Status](#status)). Nothing in this
> README reports a measured accuracy yet; numbers will be added once the
> evaluation sets exist.

## What it does

- **Document Q&A.** Upload a PDF, DOCX, TXT or Markdown file to a conversation
  and ask questions about it. Retrieval is scoped to that conversation.
- **Cited answers (in progress).** Each document answer should point to the
  file and page it came from, so you can check it.
- **Honest gaps (in progress).** If the documents don't contain the answer, the
  assistant should say so instead of guessing.
- **Web search.** The agent can look things up through Tavily when your
  documents aren't enough.
- **Long-term memory.** The agent can store and recall facts across
  conversations.
- **Accounts and history.** JWT authentication and persistent conversations.

## How an answer is produced

The model only sees what ends up in its prompt: your question, the conversation
history, and whatever the tools return. A LangGraph agent decides for each
message whether to answer directly or call a tool.

```text
Message
  -> LangGraph agent (Gemini) reads message + history
  -> decides: answer directly, or call a tool
       - document search -> top chunks from Chroma (this conversation only)
       - web search      -> Tavily results
       - memory          -> read or write stored facts
  -> tool results are added to the prompt
  -> Gemini writes the answer
  -> message saved to SQLite and returned to the frontend
```

## Status

### Available

- Create, select and delete conversations
- Persist user and assistant messages
- Chat through the FastAPI backend with a choice of configured Gemini models
- Upload PDF, DOCX, TXT and Markdown files for indexing
- Web search and long-term memory tools
- Responsive sidebar with conversation history
- Production frontend build through Vite

### In progress

- Page-level citations and a "not found" path for unanswerable questions
- Streaming assistant responses
- Conversation renaming and search
- Document management UI (list and delete indexed files)
- Automated backend and frontend tests, and CI
- Evaluation sets and published results (see below)
- Tracing, cost and latency reporting
- Rate limiting, security review and deployment configuration

## Evaluation (planned)

The goal is to measure the system instead of describing it. Results will be
published here with the question sets and scoring scripts.

| Area | What will be measured | Result |
| --- | --- | --- |
| Retrieval | Hit rate: is the correct chunk in the top 5? | Not yet measured |
| Answers | Correctness and citation correctness, scored separately from retrieval | Not yet measured |
| Unanswerable questions | How often it correctly says "not found" | Not yet measured |
| Tool selection | How often the agent picks the right tool (documents, web, memory, none) | Not yet measured |
| Cost and latency | Tokens, median and p95 response time per answer | Not yet measured |

Failures will be broken down into extraction, retrieval and generation errors.

## Technology stack

### Frontend

- React 18, TypeScript, Vite
- `lucide-react`
- CSS-based responsive styling and animations

### Backend

- Python 3.11+, FastAPI, Uvicorn
- LangChain and LangGraph
- SQLAlchemy with SQLite for local persistence and LangGraph checkpoints
- Chroma for vector search
- Google Gemini for chat and embeddings
- Tavily for web search

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
git clone https://github.com/sxb05/Pagetrail.git
Set-Location .\Pagetrail
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

`GEMINI_API_KEY` is used for chat and document embeddings. `TAVILY_API_KEY` is
used by the web-search tool. Set `JWT_SECRET_KEY` to a long, random value before
sharing or deploying the application; the built-in fallback is intended only for
local development.

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

The Vite development server proxies `/api` requests to the FastAPI server at
`http://127.0.0.1:8000`.

Create an account from the login page before using the chat workspace. Access
tokens expire after 30 minutes and are sent as Bearer tokens by the frontend.

## Production frontend build

Build the frontend:

```powershell
Set-Location .\frontend
npm run build
```

The generated files are placed in `frontend/dist`. When that directory exists,
FastAPI serves the built frontend and its assets.

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

The backend accepts the model names configured in `agent.py`; keep the frontend
model options aligned with that list.

### Document uploads

Uploads are limited to PDF, DOCX, TXT, and Markdown files smaller than 10 MB.
Files are parsed, split into chunks, and stored in the local Chroma database
with the conversation thread ID as metadata. The original uploaded file is
removed after indexing.

## Known limitations

- Answers are not streamed yet; the frontend shows a loading state.
- Citations currently identify the source file only; page-level citations are in
  progress.
- Scanned PDFs without a text layer are not supported.
- Tables in PDFs may be extracted poorly, which can affect answers about
  specifications.
- SQLite and local vector storage are intended for development, not production.

## Security notes

- Documents and web results are untrusted input. Prompt-injection handling is in
  progress and will be covered by tests.
- Retrieval is filtered by conversation; automated tests for isolation between
  users are planned.
- Do not use the development JWT secret as-is in a deployment.

## Development notes

- Local database files and vector-store data are created at runtime.
- The local application stores users, conversations, messages, and memories in
  `data/memory.db`; LangGraph checkpoints are stored in
  `data/langgraph_checkpoint.dqlite`.
- The project currently favors local development and experimentation over
  deployment hardening.

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

No project license has been defined yet. Until a license is added, treat the
repository as proprietary and obtain permission before redistributing or reusing
the code.
