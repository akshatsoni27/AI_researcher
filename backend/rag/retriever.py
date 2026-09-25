from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


CHROMA_DIR = Path("chroma_db")


def search_knowledge_base(
    query: str,
    k: int = 5,
) -> list[dict]:
    """
    Search the indexed documents for relevant evidence.
    """

    if not CHROMA_DIR.exists():
        return []

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    results = vectorstore.similarity_search(
        query,
        k=k,
    )

    evidence = []

    for document in results:
        evidence.append(
            {
                "content": document.page_content,
                "source": document.metadata.get(
                    "source",
                    "unknown",
                ),
                "page": document.metadata.get(
                    "page",
                    None,
                ),
            }
        )

    return evidence