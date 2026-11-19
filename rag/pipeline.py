
from pathlib import Path

from rag.document_loader import load_documents
from rag.text_splitter import split_documents
from rag.vector_store import create_vector_store


class DocumentValidationError(ValueError):
    """A document issue that can be explained to the user."""


def process_documents(
    file_paths: list[Path],
    vector_directory: Path,
    collection_name: str,
):
    # Load documents
    documents = load_documents(file_paths)

    if not documents:
        raise DocumentValidationError("No content found in documents.")

    # Split documents and filter metadata
    splitted_data = split_documents(documents)

    if not splitted_data:
        raise DocumentValidationError("No valid document chunks found.")

    # Create vector store
    vector_store = create_vector_store(
        documents=splitted_data,
        persist_directory=vector_directory,
        collection_name=collection_name,
    )

    return vector_store
