import streamlit as st
import requests

# Set page title and layout
st.set_page_config(page_title="Tiny LLM Chat Agent", layout="wide")
st.title("Tiny LLM Chat Agent")

# User Identification
user_id = st.text_input("Enter your user ID/name:", "")

if not user_id:
    st.warning("⚠️ Please enter a user ID before proceeding.")
    st.stop()

# File Upload Section
st.subheader("📂 Upload a PDF File to Chat with the LLM")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.write(f"✅ File selected: `{uploaded_file.name}`")

    # ✅ Upload PDF to backend
    if st.button("📤 Upload and Process PDF"):
        with st.spinner("Processing your PDF ... ⏳"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"http://rag-pipeline:8000/api/upload_pdf?user_id={user_id}", files=files)

            if response.status_code == 200:
                st.success("✅ PDF uploaded and processed successfully! You can now ask questions.")
            else:
                st.error(f"❌ Error processing PDF, please try again in a few seconds. Error: {response.text}")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
st.subheader("💬 Chat with the LLM")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input for Chat
prompt = st.chat_input("Type your message...")

if prompt:
    # Store & Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send Prompt to Backend
    with st.spinner("Thinking ... 💭"):
        response = requests.post(
            url=f"http://rag-pipeline:8000/api/chat?user_id={user_id}",
            json={"messages": prompt}
        )

        # Handle Response
        if response.status_code == 200:
            ai_response = response.json()["response"]
        else:
            ai_response = "❌ Error fetching response from API. Please try to reload the LLM model."

    # Store & Display AI Response
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
