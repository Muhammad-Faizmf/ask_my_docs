
import streamlit as st
from ui.service_errors import model_service_message


def render_chat():
    st.title("Ask My Docs")
    st.caption("Ask questions about your uploaded documents.")

    if st.button("Upload New Documents"):
        st.session_state.agent = None
        st.session_state.vector_store = None
        st.session_state.document_uploaded = False
        st.session_state.messages = []
        st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input(
        "Ask anything about your documents..."
    )

    if not user_input:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                agent = st.session_state.agent

                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input,
                            }
                        ]
                    },
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id
                        }
                    },
                )

                answer = response["messages"][-1].content

                if isinstance(answer, list):
                    answer = " ".join(
                        part.get("text", "")
                        for part in answer
                        if isinstance(part, dict)
                        and part.get("type") == "text"
                    )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as error:
                st.error(
                    model_service_message(error, "answer your question")
                    or "Unable to generate an answer. Please try again."
                )
