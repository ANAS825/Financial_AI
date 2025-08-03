import streamlit as st
import PyPDF2
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment variables if needed
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),  
)

# Streamlit UI setup
st.set_page_config(page_title="Financial Document Analysis", page_icon="📊", layout="centered")
st.header("💹 Financial Document Analysis with AI")
st.markdown("Upload financial documents in PDF or TXT format and analyze them using AI.")

chat_input = st.chat_input("Ask a question about the uploaded documents:", accept_file=True, file_type=["pdf", "txt"], on_submit=None, key="chat_input")

# PDF reader function
def process_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Extract content from uploaded files
def extract_txt_from_file(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        return process_pdf(io.BytesIO(file.read()))
    else:
        raise ValueError("Unsupported file type")

# Initialize chat history if not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# Main logic
try:
    data = st.session_state.get("chat_input", {})
    
    if not data:
        pass

    elif not data.get('files'):
        user_question = data.get("text", "")

        # Build context prompt
        prompt = f"You are a financial analysis AI assistant. Your job is to give insight to the user based on their question. The user question is: {user_question}. Provide clear, concise insights in a professional tone."

        # Combine with previous history
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        messages.append({"role": "user", "content": prompt})

        # Call model
        response = client.chat.completions.create(
            messages=messages,
            model="deepseek/deepseek-chat-v3-0324:free",
            temperature=0.5,
            top_p=1.0,
            max_tokens=2048
        )

        # Extract AI response
        full_response = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

        # Animated display
        placeholder = st.empty()
        typed_text = ""
        for chunk in full_response.split(" "):  
            typed_text += chunk + " "
            placeholder.markdown("### AI Response:\n" + typed_text)
            time.sleep(0.05)

    else:
        files = data.get("files", [])
        file = files[0]
        file_content = extract_txt_from_file(file)

        if not file_content.strip():
            st.error('Please upload a valid file with content.')

        user_question = data.get("text", "")

        prompt = f"""
You are a financial analysis AI assistant. Your job is to analyze or summarize billing documents, financial statements, or any uploaded financial reports.

Extract key insights such as revenue trends, expenses, profit margins, unusual activity, debt levels, or investment details.

Based on the uploaded document, do the following:

- Summarize key financial information — highlight revenue, profit/loss, operating costs, debts, cash flows, and significant changes over time.
- Identify red flags or noteworthy patterns — such as rising debts, expense spikes, or unusual transactions.
- Answer user questions based on the content of the document.
- Provide clear, concise insights in a professional tone.

The uploaded document content is as follows:
{file_content.strip()}

User question: {user_question if user_question else "No specific question asked."}
"""

        # Combine with previous history
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            messages=messages,
            model="deepseek/deepseek-r1-distill-qwen-7b",
            temperature=0.5,
            top_p=1.0,
            max_tokens=2048
        )

        full_response = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

        # Display response
        placeholder = st.empty()
        typed_text = ""
        for chunk in full_response.split(" "):  
            typed_text += chunk + " "
            placeholder.markdown("### AI Response:\n" + typed_text)
            time.sleep(0.05)

except Exception as e:
    st.error(f"Something went wrong: {str(e)}")
