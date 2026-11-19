
from pathlib import Path
from langchain_chroma import Chroma
from rag.embeddings import get_embeddings


def create_vector_store(
    documents,
    persist_directory: Path,
    collection_name: str = "documents",
):
    persist_directory.mkdir(parents=True, exist_ok=True)

    return Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        persist_directory=str(persist_directory),
        collection_name=collection_name,
    )
