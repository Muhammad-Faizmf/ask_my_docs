
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


def split_documents(documents):
    # Text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    splitted_data = splitter.split_documents(documents)

    # Remove metadata which are not JSON serializable
    for doc in splitted_data:
        doc.metadata = {
            k: v for k, v in doc.metadata.items()
            if isinstance(v, (str, int, float, bool))
        }

    return splitted_data
