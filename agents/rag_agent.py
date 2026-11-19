
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from config import GROQ_MODEL, GROQ_API_KEY
from agents.prompts import SYSTEM_PROMPT
from agents.tools import create_retrieval_tool


def build_rag_agent(vector_store):
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
    )

    retrieval_tool = create_retrieval_tool(vector_store)

    memory = InMemorySaver()

    agent = create_agent(
        model=llm,
        tools=[retrieval_tool],
        checkpointer=memory,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
