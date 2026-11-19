
from pathlib import Path
from threading import Lock

import nltk
from langchain_unstructured import UnstructuredLoader

_nltk_download_lock = Lock()


def ensure_nltk_resources():
    """Use the official NLTK downloader before Unstructured partitions a PDF."""
    with _nltk_download_lock:
        for resource in (
            "tokenizers/punkt_tab",
            "taggers/averaged_perceptron_tagger_eng",
        ):
            try:
                nltk.data.find(resource)
            except LookupError:
                nltk.download(resource.rsplit("/", 1)[-1], quiet=True, raise_on_error=True)
                nltk.data.find(resource)


def load_documents(file_paths: list[Path]):
    if file_paths:
        ensure_nltk_resources()

    documents = []

    for file_path in file_paths:
        loader = UnstructuredLoader(str(file_path))
        loaded_docs = loader.load()

        for doc in loaded_docs:
            doc.metadata["source"] = file_path.name

        documents.extend(loaded_docs)

    return documents
