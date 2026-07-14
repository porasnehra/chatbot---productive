import streamlit as st
import requests
import uuid

st.set_page_config(page_title="AI Virtual Event Manager", layout="centered")

# --- 1. Initialize Multi-Thread Chat Storage ---
if "chats" not in st.session_state:
    # Create the first default chat session with a unique thread ID
    default_id = str(uuid.uuid4())
    st.session_state.chats = {
        "Chat 1": {"thread_id": default_id, "messages": []}
    }
    st.session_state.current_chat = "Chat 1"
    st.session_state.chat_counter = 1

st.title("AI Virtual Event Manager")

with st.sidebar:
    st.header("Upload Menu & Policy")
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    
    if st.button("Process Document"):
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            with st.spinner("Processing PDF..."):
                # Make sure to use your Render backend URL here if deployed
                res = requests.post("https://chatbot-productive.onrender.com/upload_pdf", files=files)
            if res.status_code == 200:
                st.success("Document uploaded and indexed successfully!")
            else:
                st.error("Failed to upload the document.")
        else:
            st.warning("Please select a PDF file first.")
            
    st.divider()
    
    # --- 2. Chat History Sidebar Controls ---
    st.header("Chat History")
    
    # Button to start a completely new thread
    if st.button("➕ New Chat"):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        
        # Assign a brand new unique thread_id for the backend
        st.session_state.chats[new_chat_name] = {
            "thread_id": str(uuid.uuid4()), 
            "messages": []
        }
        # Automatically switch to the newly created chat
        st.session_state.current_chat = new_chat_name

    # Radio buttons to select between existing chat sessions
    chat_names = list(st.session_state.chats.keys())
    selected_chat = st.radio(
        "Select a conversation:", 
        chat_names, 
        index=chat_names.index(st.session_state.current_chat)
    )
    
    # If the user clicks a different chat, update the state
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat

# --- 3. Load Active Chat Data ---
# Fetch the thread_id and visual messages for whatever chat is currently selected
active_chat = st.session_state.chats[st.session_state.current_chat]
active_thread_id = active_chat["thread_id"]
active_messages = active_chat["messages"]

# Display the visual history for the currently selected chat thread
for msg in active_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about estimates, guest rules, or menu policies...")

if user_input:
    # Save the user's prompt to the specific active thread's visual history
    active_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Send the exact active_thread_id to the backend so the AI knows the context
        payload = {
            "thread_id": active_thread_id,
            "message": user_input
        }
        with st.spinner("Calculating & Checking Policies..."):
            # Make sure to use your Render backend URL here if deployed
            res = requests.post("https://chatbot-productive.onrender.com/chat", json=payload)
            
        if res.status_code == 200:
            answer = res.json().get("response")
            st.markdown(answer)
            # Save the AI's response to the specific active thread's visual history
            active_messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Backend error occurred.")
