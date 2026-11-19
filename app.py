import uuid
from threading import Lock
import streamlit as st
from ui.upload import render_upload
from ui.chat import render_chat

st.set_page_config(
    page_title="Ask My Docs",
    page_icon="📚",
    layout="centered",
)

def initialize_session():
    defaults = {
        "session_id": str(uuid.uuid4()),
        "thread_id": str(uuid.uuid4()),
        "document_uploaded": False,
        "agent": None,
        "vector_store": None,
        "messages": [],
        "processing_lock": Lock(),
        "process_button_key": str(uuid.uuid4()),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    initialize_session()

    if (
        st.session_state.document_uploaded
        and st.session_state.agent is not None
    ):
        render_chat()
    else:
        render_upload()

if __name__ == "__main__":
    main()
