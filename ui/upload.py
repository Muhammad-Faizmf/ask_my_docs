
import logging
import re
import shutil
import uuid
from pathlib import Path
import streamlit as st
from config import GOOGLE_API_KEY, GROQ_API_KEY, MAX_UPLOAD_MB, UPLOAD_DIR, VECTOR_DIR
from rag.pipeline import DocumentValidationError, process_documents
from agents.rag_agent import build_rag_agent
from ui.service_errors import model_service_message

logger = logging.getLogger(__name__)


def render_upload():
    st.title("Ask My Docs")
    st.write("Upload PDF documents and ask questions using AI.")

    uploaded_files = st.file_uploader(
        "Upload your PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        return

    processing_lock = st.session_state.processing_lock
    button_slot = st.empty()
    if processing_lock.locked():
        button_slot.button("Processing...", disabled=True, key="process_documents_busy")
        # A rerun can arrive while the previous script is still inside a provider call.
        with processing_lock:
            pass
        st.rerun()

    if not button_slot.button(
        "Process Documents",
        type="primary",
        key=st.session_state.process_button_key,
    ):
        return

    if not processing_lock.acquire(blocking=False):
        return

    try:
        # Replace the prior button identity so queued clicks can't start another run.
        st.session_state.process_button_key = str(uuid.uuid4())
        button_slot.button(
            "Processing...",
            type="primary",
            disabled=True,
            key="process_documents_busy",
        )
        processed = process_uploaded_files(uploaded_files)
    finally:
        processing_lock.release()

    if processed:
        st.rerun()

    button_slot.button(
        "Process Documents",
        type="primary",
        key=st.session_state.process_button_key,
    )


def process_uploaded_files(uploaded_files):
    missing_keys = [
        name
        for name, value in (
            ("GOOGLE_API_KEY", GOOGLE_API_KEY),
            ("GROQ_API_KEY", GROQ_API_KEY),
        )
        if not value
    ]
    if missing_keys:
        logger.error("Missing API configuration: %s", ", ".join(missing_keys))
        st.error("The AI service is missing its API configuration. Contact the app administrator.")
        return False

    session_id = st.session_state.session_id

    upload_directory = UPLOAD_DIR / session_id
    vector_directory = VECTOR_DIR / session_id

    saved_paths = []

    stage = "save uploads"
    try:
        with st.spinner("Processing documents..."):
            # Clear previous data for this session
            if upload_directory.exists():
                shutil.rmtree(upload_directory)

            if vector_directory.exists():
                shutil.rmtree(vector_directory)

            upload_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.getvalue()

                if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
                    raise DocumentValidationError(
                        f"{uploaded_file.name} exceeds "
                        f"{MAX_UPLOAD_MB} MB."
                    )

                if not file_bytes.startswith(b"%PDF-"):
                    raise DocumentValidationError(
                        f"{uploaded_file.name} is not a valid PDF."
                    )

                # Prevent unsafe filename paths
                original_name = Path(
                    uploaded_file.name.replace("\\", "/")
                ).name

                safe_name = re.sub(
                    r"[^a-zA-Z0-9._-]",
                    "_",
                    original_name,
                )

                unique_name = (
                    f"{uuid.uuid4().hex[:8]}_{safe_name}"
                )

                saved_path = upload_directory / unique_name
                saved_path.write_bytes(file_bytes)

                saved_paths.append(saved_path)

            stage = "extract and index documents"
            vector_store = process_documents(
                file_paths=saved_paths,
                vector_directory=vector_directory,
                collection_name="documents",
            )

            stage = "initialize chat"
            agent = build_rag_agent(vector_store)

            st.session_state.agent = agent
            st.session_state.vector_store = vector_store
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.document_uploaded = True

        return True

    except DocumentValidationError as error:
        st.error(str(error))
    except ImportError as error:
        logger.error("Dependency import failed during %s: %s", stage, error)
        st.error(
            "Document processing is unavailable because a server dependency "
            "could not load. Contact the app administrator."
        )
    except Exception as error:
        cause = error.__cause__ or error
        logger.error(
            "Document processing failed during %s (%s, status=%s)",
            stage,
            type(cause).__name__,
            getattr(cause, "status_code", getattr(cause, "code", None)),
        )
        st.error(
            model_service_message(error, "process your documents")
            or "Unable to process your documents. Please try again."
        )
    return False
