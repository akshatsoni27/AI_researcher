from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from backend.rag.loader import load_pdf


CHROMA_DIR = Path("chroma_db")


def create_vectorstore(pdf_path: str):
    """
    Load a PDF, create embeddings, and store them in Chroma.
    """

    chunks = load_pdf(pdf_path)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    return vectorstore