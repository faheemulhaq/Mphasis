from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import docx
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import pyttsx3
import speech_recognition as sr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
secret_key = os.urandom(24)
app.secret_key = secret_key # Replace with a secure key

# In-memory user database (replace with a real database)
users_db = {}

# Store user sessions (simple implementation)
user_sessions = {}

# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if email in users_db:
        return jsonify({"status": "error", "message": "Email already exists"}), 400
    users_db[email] = password
    return jsonify({"status": "success", "message": "User registered successfully"}), 200

# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if users_db.get(email) == password:
        # Simple session management
        user_sessions[email] = True
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# Endpoint to process documents
@app.route('/process_documents', methods=['POST'])
def process_documents():
    email = request.form.get('email')
    if not user_sessions.get(email):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    files = request.files.getlist('documents')
    if not files:
        return jsonify({"status": "error", "message": "No files uploaded"}), 400

    raw_text = ""
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.endswith('.pdf'):
            raw_text += get_pdf_text(file_path)
        elif filename.endswith('.docx'):
            raw_text += get_docx_text(file_path)
        elif filename.endswith('.xlsx'):
            raw_text += get_excel_text(file_path)

    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

    return jsonify({"status": "success", "message": "Documents processed successfully"}), 200

# Endpoint to handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    email = data.get('email')
    user_message = data.get('message')
    if not user_sessions.get(email):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    response = user_input(user_message)
    return jsonify({"response": response}), 200

# Function definitions (similar to your Dexter.py)

def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_docx_text(docx_path):
    text = ""
    doc_reader = docx.Document(docx_path)
    for para in doc_reader.paragraphs:
        text += para.text + "\n"
    return text

def get_excel_text(excel_path):
    text = ""
    df = pd.read_excel(excel_path)
    text += df.to_string(index=False)
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in
    the provided context, just say, "Answer is not available in the context." Do not provide a wrong answer.\n\n
    Context:\n {context}\n
    Question: \n{question}\n
    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_serialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return response["output_text"]

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(port=5000, debug=True)