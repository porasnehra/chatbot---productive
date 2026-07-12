import streamlit as st
import requests
import uuid

st.set_page_config(page_title="AI Virtual Event Manager", layout="centered")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("AI Virtual Event Manager")

with st.sidebar:
    st.header("Upload Menu & Policy")
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    
    if st.button("Process Document"):
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            with st.spinner("Processing PDF..."):
                res = requests.post("http://127.0.0.1:8000/upload_pdf", files=files)
            if res.status_code == 200:
                st.success("Document uploaded and indexed successfully!")
            else:
                st.error("Failed to upload the document.")
        else:
            st.warning("Please select a PDF file first.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about estimates, guest rules, or menu policies...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        payload = {
            "thread_id": st.session_state.thread_id,
            "message": user_input
        }
        with st.spinner("Calculating & Checking Policies..."):
            res = requests.post("http://127.0.0.1:8000/chat", json=payload)
            
        if res.status_code == 200:
            answer = res.json().get("response")
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Backend error occurred.")
