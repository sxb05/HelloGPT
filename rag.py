from pathlib import Path
from dotenv import load_dotenv
from typing import List
import os

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pypdf import PdfReader
import docx2txt


load_dotenv()

Path("uploads").mkdir(exist_ok=True)
Path("chroma_db").mkdir(exist_ok=True)

embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")

vector_store = Chroma(
    collection_name = "chatbot_docs",
    embedding_function = embeddings,
    persist_directory = "chroma_db"
)


def read_pdf(file_path: str) -> str:
    """
    Read a PDF file and return its text content.
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        pdf_reader = PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text
    if suffix == ".docx":
        text = docx2txt.process(file_path)
        return text 
    if suffix in [ ".txt", ".md"]:
        return file_path.read_text(encoding="utf-8", errors = "ignore")

    raise ValueError(f"Unsupported file type: {suffix}, Please provide a PDF, DOCX, TXT, or MD file.") 


def add_document_to_vector_store(file_path: str, thread_id: str):
    """
    Read a document, split it into chunks, and add it to the vector store.
    """
    text = read_pdf(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    documents: List[Document] = [
        Document(
            page_content=chunk,
            metadata={"thread_id": thread_id, "source": Path(file_path).name},
        )
        for chunk in chunks
    ]
    
    vector_store.add_documents(documents)

    return{ "filename" : Path(file_path).name, "num_chunks": len(chunks)}
def retrieve_documents(query: str, thread_id: str, k: int = 5):
    """
    Retrieve documents from the vector store based on a query and thread_id.
    """
    results = vector_store.similarity_search(query, k=k, filter={"thread_id": thread_id})
    if not results:
        return "No relevant documents found."
    results=[]
    for i , doc in enumerate(results, start=1):
        results.append({"chunk_index": i, "content": doc.page_content, "metadata": doc.metadata})
    return results