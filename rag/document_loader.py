
from pathlib import Path
from langchain_unstructured import UnstructuredLoader


def load_documents(file_paths: list[Path]):
    documents = []

    for file_path in file_paths:
        loader = UnstructuredLoader(str(file_path))
        loaded_docs = loader.load()

        for doc in loaded_docs:
            doc.metadata["source"] = file_path.name

        documents.extend(loaded_docs)

    return documents
