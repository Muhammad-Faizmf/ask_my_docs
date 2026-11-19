
from langchain_core.tools import tool


def create_retrieval_tool(vector_store):

    @tool
    def retrieve_context(query: str) -> str:
        """Retrieve relevant information from uploaded documents."""

        docs = vector_store.similarity_search(
            query=query,
            k=4
        )

        if not docs:
            return "No relevant context found."

        return "\n\n".join(
            doc.page_content for doc in docs
        )

    return retrieve_context
