
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import EMBEDDING_MODEL ,GOOGLE_API_KEY

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        api_key=GOOGLE_API_KEY,
        model=EMBEDDING_MODEL
    )