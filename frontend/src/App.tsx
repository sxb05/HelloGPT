import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  ArrowUp,
  ChevronDown,
  Copy,
  FileText,
  LogOut,
  Menu,
  MessageSquare,
  MoreHorizontal,
  Paperclip,
  Plus,
  Search,
  ThumbsDown,
  ThumbsUp,
  X,
} from "lucide-react";

type Conversation = { thread_id: string; name: string; updated_at?: string };
type ChatMessage = { role: "user" | "assistant"; content: string };

const starterPrompts = [
  { title: "Plan a project", text: "Help me plan a project from idea to launch" },
  { title: "Explain a concept", text: "Explain a complex concept in simple terms" },
  { title: "Write something", text: "Help me write a polished professional email" },
];

function OpenAiLogoIcon({ size = 20 }: { size?: number }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      fill="currentColor"
      viewBox="0 0 256 256"
    >
      <path d="M224.32,114.24a56,56,0,0,0-60.07-76.57A56,56,0,0,0,67.93,51.44a56,56,0,0,0-36.25,90.32A56,56,0,0,0,69,217,56.39,56.39,0,0,0,83.59,219a55.75,55.75,0,0,0,8.17-.61,56,56,0,0,0,96.31-13.78,56,56,0,0,0,36.25-90.32ZM182.85,54.43a40,40,0,0,1,28.56,48c-.95-.63-1.91-1.24-2.91-1.81L164,74.88a8,8,0,0,0-8,0l-44,25.41V81.81l40.5-23.38A39.76,39.76,0,0,1,182.85,54.43ZM144,137.24l-16,9.24-16-9.24V118.76l16-9.24,16,9.24ZM80,72a40,40,0,0,1,67.53-29c-1,.51-2,1-3,1.62L100,70.27a8,8,0,0,0-4,6.92V128l-16-9.24ZM40.86,86.93A39.75,39.75,0,0,1,64.12,68.57C64.05,69.71,64,70.85,64,72v51.38a8,8,0,0,0,4,6.93l44,25.4L96,165,55.5,141.57A40,40,0,0,1,40.86,86.93ZM73.15,201.57a40,40,0,0,1-28.56-48c.95.63,1.91,1.24,2.91,1.81L92,181.12a8,8,0,0,0,8,0l44-25.41v18.48l-40.5,23.38A39.76,39.76,0,0,1,73.15,201.57ZM176,184a40,40,0,0,1-67.52,29.05c1-.51,2-1.05,3-1.63L156,185.73a8,8,0,0,0,4-6.92V128l16,9.24Zm39.14-14.93a39.75,39.75,0,0,1-23.26,18.36c.07-1.14.12-2.28.12-3.43V132.62a8,8,0,0,0-4-6.93l-44-25.4,16-9.24,40.5,23.38A40,40,0,0,1,215.14,169.07Z" />
    </svg>
  );
}

function App() {

  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    return !!localStorage.getItem("user_token");
  });

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [model, setModel] = useState("gemini-3.1-flash-lite");
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

   const handleLogin = (e: FormEvent) => {
    e.preventDefault();
    // Simulate a successful login token creation
    localStorage.setItem("user_token", "dummy-secret-session-key");
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("user_token");
    setIsLoggedIn(false);
    setConversations([]);
    setMessages([]);
    setThreadId(null);
    setAccountMenuOpen(false);
  };

  useEffect(() => {
    if (!isLoggedIn) return;
    fetch("/api/conversations")
      .then((response) => (response.ok ? response.json() : []))
      .then((data: Conversation[]) => setConversations(data))
      .catch(() => undefined);
  }, [isLoggedIn]);

  useEffect(() => {
    if (!isLoggedIn) return;
    const sharedThreadId = new URLSearchParams(window.location.search).get("conversation");
    if (sharedThreadId && conversations.some((conversation) => conversation.thread_id === sharedThreadId)) {
      void selectConversation(sharedThreadId);
    }
  }, [conversations, isLoggedIn]);

  useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages, loading]);


  async function selectConversation(id: string) {
    setThreadId(id);
    setSidebarOpen(false);
    setError("");
    setOpenMenuId(null);
    const response = await fetch(`/api/conversations/${id}/messages`);
    if (response.ok) setMessages(await response.json());
  }

  async function shareConversation(conversation: Conversation) {
    const shareUrl = `${window.location.origin}/?conversation=${encodeURIComponent(conversation.thread_id)}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setError(`Share link copied for "${conversation.name}".`);
    } catch {
      setError("Could not copy the share link. Please copy the page URL manually.");
    }
    setOpenMenuId(null);
  }

  async function removeConversation(conversation: Conversation) {
    if (!window.confirm(`Delete "${conversation.name}"? This cannot be undone.`)) return;
    const response = await fetch(`/api/conversations/${conversation.thread_id}`, { method: "DELETE" });
    if (!response.ok) {
      setError("Unable to delete this conversation.");
      return;
    }
    setConversations((current) => current.filter((item) => item.thread_id !== conversation.thread_id));
    if (threadId === conversation.thread_id) {
      setThreadId(null);
      setMessages([]);
    }
    setOpenMenuId(null);
  }

  async function newChat() {
    const response = await fetch("/api/conversations", { method: "POST" });
    if (!response.ok) return;
    const conversation: Conversation = await response.json();
    setConversations((current) => [conversation, ...current]);
    setThreadId(conversation.thread_id);
    setMessages([]);
    setError("");
    setSidebarOpen(false);
  }

  async function submitMessage(event?: FormEvent) {
    event?.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    let activeThread = threadId;
    if (!activeThread) {
      const response = await fetch("/api/conversations", { method: "POST" });
      if (!response.ok) return;
      const conversation: Conversation = await response.json();
      activeThread = conversation.thread_id;
      setThreadId(activeThread);
      setConversations((current) => [conversation, ...current]);
    }
    setInput("");
    setError("");
    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setLoading(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: activeThread, message: trimmed, model }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Something went wrong.");
      setMessages((current) => [...current, data]);
      setConversations((current) =>
        current.map((conversation) =>
          conversation.thread_id === activeThread
            ? { ...conversation, name: trimmed.slice(0, 48), updated_at: new Date().toISOString() }
            : conversation,
        ),
      );
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to send message.");
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(file: File) {
    let activeThread = threadId;
    if (!activeThread) {
      const response = await fetch("/api/conversations", { method: "POST" });
      if (!response.ok) return;
      const conversation: Conversation = await response.json();
      activeThread = conversation.thread_id;
      setThreadId(activeThread);
      setConversations((current) => [conversation, ...current]);
    }
    
    
    
    if (!activeThread) return;
    setFileName(file.name);
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`/api/conversations/${activeThread}/files`, { method: "POST", body: form });
    if (!response.ok) setError("This file could not be added to the conversation.");
  }
  
  if (!isLoggedIn) {
    return (
      <main className="login-page">
        <div className="login-glow login-glow--top" aria-hidden="true" />
        <div className="login-glow login-glow--bottom" aria-hidden="true" />
        <section className="login-card" aria-labelledby="login-title">
          <div className="login-brand">
            <span className="brand-mark"><OpenAiLogoIcon size={21} /></span>
            <span>HelloGPT</span>
          </div>
          <div className="login-heading">
            <div className="login-orb" aria-hidden="true">
              <OpenAiLogoIcon size={30} />
            </div>
            <p className="login-eyebrow">Your thoughtful AI workspace</p>
            <h1 id="login-title">Welcome back</h1>
            <p>Sign in to continue your conversations, ideas, and work.</p>
          </div>
          <form onSubmit={handleLogin}>
            <button type="submit" className="login-button">
              <span>Continue to HelloGPT</span>
              <ArrowUp size={17} />
            </button>
          </form>
          <p className="login-note">By continuing, you agree to use HelloGPT responsibly.</p>
        </section>
      </main>
    );
  }
  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar-top">
          <button className="brand" onClick={newChat} aria-label="Start a new chat">
            <span className="brand-mark"><OpenAiLogoIcon size={18} /></span>
            <span>HelloGPT</span>
          </button>
          <button className="icon-button sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar"><X size={18} /></button>
        </div>
        <button className="new-chat" onClick={newChat}><Plus size={17} /> New chat <span className="shortcut">Ctrl K</span></button>
        <div className="sidebar-search"><Search size={16} /><input placeholder="Search chats" /></div>
        <div className="history-heading">Your chats <MoreHorizontal size={17} /></div>
        <nav className="history-list">
          {conversations.length === 0 && <p className="empty-history">Your recent conversations will appear here.</p>}
          {conversations.map((conversation) => (
            <div key={conversation.thread_id} className={`history-item ${conversation.thread_id === threadId ? "active" : ""}`}>
              <button className="history-select" onClick={() => selectConversation(conversation.thread_id)}>
                <MessageSquare size={15} /><span>{conversation.name}</span>
              </button>
              <button
                className="history-menu-button"
                aria-label={`Actions for ${conversation.name}`}
                aria-expanded={openMenuId === conversation.thread_id}
                onClick={(event) => {
                  event.stopPropagation();
                  setOpenMenuId((current) => current === conversation.thread_id ? null : conversation.thread_id);
                }}
              >
                <MoreHorizontal size={17} />
              </button>
              {openMenuId === conversation.thread_id && (
                <div className="history-menu">
                  <button onClick={() => shareConversation(conversation)}><Copy size={14} /> Share</button>
                  <button className="danger" onClick={() => removeConversation(conversation)}><X size={14} /> Delete</button>
                </div>
              )}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="account-menu-wrap">
            <button
              className="account-card"
              aria-label="Open account menu"
              aria-expanded={accountMenuOpen}
              aria-haspopup="menu"
              onClick={() => setAccountMenuOpen((current) => !current)}
            >
              <span className="avatar">S</span>
              <span><strong>Rahul</strong><small>Free plan</small></span>
              <MoreHorizontal size={17} />
            </button>
            {accountMenuOpen && (
              <div className="account-menu" role="menu">
                <button
                  className="danger"
                  role="menuitem"
                  onClick={handleLogout}
                >
                  <LogOut size={14} /> Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>
      {sidebarOpen && <button className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar" />}
      <main className="main-panel">
        <header className="topbar">
          <button className="icon-button menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar"><Menu size={19} /></button>
          <button className="model-picker" onClick={() => setModel(model === "gemini-3.1-flash-lite" ? "gemini-2.5-flash" : "gemini-3.1-flash-lite")}>
            <span className="status-dot" /> {model === "gemini-3.1-flash-lite" ? "HelloGPT" : "HelloGPT Fast"} <ChevronDown size={15} />
          </button>
          <div className="topbar-actions"><button className="icon-button" aria-label="Share chat"><MoreHorizontal size={19} /></button><button className="avatar small">R</button></div>
        </header>
        <section className={`chat-stage ${messages.length ? "chat-stage--active" : ""}`}>
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-orb"><OpenAiLogoIcon size={29} /></div>
              <h1>How can I help you today?</h1>
              <p>Thoughtful answers, useful ideas, and a little extra clarity.</p>
              <div className="prompt-grid">{starterPrompts.map((prompt) => <button key={prompt.title} className="prompt-card" onClick={() => setInput(prompt.text)}><span>{prompt.title}</span><small>{prompt.text}</small><ArrowUp size={15} /></button>)}</div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message, index) => <Message key={`${message.role}-${index}`} message={message} />)}
              {loading && <div className="message-row assistant"><div className="assistant-avatar"><OpenAiLogoIcon size={15} /></div><div className="typing"><i /><i /><i /></div></div>}
              <div ref={bottomRef} />
            </div>
          )}
          {error && <div className="error-banner">{error}</div>}
          <form className="composer-wrap" onSubmit={submitMessage}>
            {fileName && <div className="file-chip"><FileText size={14} /> {fileName}<button type="button" onClick={() => setFileName("")}><X size={13} /></button></div>}
            <div className="composer">
              <input ref={fileRef} type="file" accept=".pdf,.docx,.txt,.md" hidden onChange={(event) => event.target.files?.[0] && uploadFile(event.target.files[0])} />
              <button type="button" className="composer-button" onClick={() => fileRef.current?.click()} aria-label="Attach file"><Paperclip size={19} /></button>
              <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Message HelloGPT..." aria-label="Message HelloGPT" />
              <button className={`send-button ${input.trim() ? "send-button--ready" : ""}`} aria-label="Send message" disabled={!input.trim() || loading}><ArrowUp size={17} /></button>
            </div>
            <p className="composer-note">HelloGPT can make mistakes. Check important info.</p>
          </form>
        </section>
      </main>
    </div>
  );
}

function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return <div className={`message-row ${isUser ? "user" : "assistant"}`}>
    {isUser ? <div className="avatar message-avatar">R</div> : <div className="assistant-avatar"><OpenAiLogoIcon size={15} /></div>}
    <div className="message-content"><div className="message-role">{isUser ? "You" : "HelloGPT"}</div><div className="message-text">{message.content}</div>{!isUser && <div className="message-actions"><button aria-label="Copy response"><Copy size={14} /></button><button aria-label="Good response"><ThumbsUp size={14} /></button><button aria-label="Bad response"><ThumbsDown size={14} /></button></div>}</div>
  </div>;
}

export default App;
