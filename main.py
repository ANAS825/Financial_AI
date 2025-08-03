import streamlit as st
import PyPDF2
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import time


# Load environment variables
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= os.getenv("API_KEY")
)


# Streamlit UI  
st.set_page_config(page_title="Financial Document Analysis", page_icon="📊", layout="centered")
st.header("💹 Financial Document Analysis with AI")
st.markdown("Upload financial documents in PDF or TXT format and analyze them using AI.")

chat_input = st.chat_input("Ask a question about the uploaded documents:", accept_file=True, file_type=["pdf", "txt"], on_submit=None, key="chat_input")

# PDF reader
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

# Main logic
try:

    data = st.session_state.get("chat_input", {})
    if not data:
        pass


    elif not data.get('files'):
        user_question = data.get("text", "")

        prompt = f"You are a financial analysis AI assistant. Your job is to give insight to the user based on their question. The user question is: {user_question }. Provide clear, concise insights in a professional tone."
        response = client.chat.completions.create(
            messages=[
                    {"role": "system", "content": "You are a highly skilled financial analyst AI assistant. Answer the user question based on your knowledge."},
                    {"role": "user", "content": prompt}
                ],
                model = "deepseek/deepseek-chat-v3-0324:free",
                temperature=0.5,
                top_p=1.0,
                max_tokens=2048
        )
        # Display the response
        st.markdown("### AI Response:")
        placeholder = st.empty()
        full_response = response.choices[0].message.content
        typed_text = ""

        for chunk in full_response.split(" "):  
            typed_text += chunk + " "
            placeholder.markdown("### Ai Response:\n" + typed_text)
            time.sleep(0.05)  

    else:
        files = data.get("files", [])
        file = files[0]
        file_content = extract_txt_from_file(file)

        if not file_content.strip():
            st.error('Please upload a valid file with content.')

        user_question = data.get("text", "")

        prompt = f"""
You are a financial analysis AI assistant. Your job is to analyze billing documents, financial statements, or any uploaded financial reports. 
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

        response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a highly skilled financial analyst AI assistant. Analyze the document, extract key insights, and answer the user question"},
            {"role": "user", "content": prompt}
        ],
        model="deepseek/deepseek-r1-distill-qwen-7b",  
        temperature=0.5,
        top_p=1.0,
        max_tokens=2048,
)

        # Display the response
        st.markdown("### Financial Document Analysis:")
        placeholder = st.empty()
        full_response = response.choices[0].message.content
        typed_text = ""

        for chunk in full_response.split(" "):  
            typed_text += chunk + " "
            placeholder.markdown(typed_text)
            time.sleep(0.05)  

    

except Exception as e:
        st.error(f"Something went wrong: {str(e)}")