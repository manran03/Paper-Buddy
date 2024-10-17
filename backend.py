import os
import io
import base64
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from flask_cors import CORS
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app)

# Initialize global variables
vector_store = None

# Define functions
def get_pdf_text_from_base64(pdf_base64):
    pdf_bytes = base64.b64decode(pdf_base64)
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def create_vector_store(text_chunks):
    global vector_store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def user_input(user_question):
    global vector_store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if vector_store is None:
        return "Please upload and process PDFs first."
    else:
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        return docs

def process_function(function_id, context, user_input, docs):

    prompt_templates = {
        0: """
        Answer the question using only the information from the provided context. If the answer is not in the context, state: "Answer is not available in the context."

        Context:
        {context}

        Question:
        {question}

        Answer:
        """,
        1: """
        Rate the quality of the paper based on the provided context on a scale from 1 to 10.

        Context:
        {context}

        Question:
        {question}

        Quality Rating:
        """,
        2: """
        Summarize the most important points from the paper based on the provided context.

        Context:
        {context}

        Question:
        {question}

        Important Points:
        """,
        3: """
        Rate the readability of the paper based on the provided context on a scale from 1 to 10.

        Context:
        {context}

        Question:
        {question}

        Readability Rating:
        """
    }

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_templates[function_id], input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    response = chain({"context": context, "question": user_input, "input_documents": docs})

    return response["output_text"].strip() if "output_text" in response else "Error: No valid response."

def select_function(user_prompt):
    function_prompt = """
    Based on the user's prompt, decide which function to call. The available functions are:

    1. Rate the quality of the paper.
    2. Extract the most important points of the paper.
    3. Rate the readability of the paper.

    If none of the functions are suitable, respond with "none".

    User Prompt:
    {user_prompt}

    Function to call:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    response = model.invoke([
        {"role": "system", "content": function_prompt},
        {"role": "user", "content": user_prompt}
    ])

    output_text = response.content if response.content else "Error: No valid response."

    if "3" in output_text or "readability" in output_text.lower():
        return 3
    elif "2" in output_text or "important points" in output_text.lower():
        return 2
    elif "1" in output_text or "quality" in output_text.lower():
        return 1
    else:
        return 0

@app.route("/process_pdf", methods=["POST"])
def process_pdf():
    data = request.json
    pdf_base64 = data.get("pdf_base64")
    query = data.get("query")

    if not pdf_base64 or not query:
        return jsonify({"error": "Please provide both PDF and query"}), 400

    # Process the PDF
    try:
        raw_text = get_pdf_text_from_base64(pdf_base64)
        text_chunks = get_text_chunks(raw_text)
        create_vector_store(text_chunks)
        docs = user_input(query)

        # Select the appropriate function based on query
        function_id = select_function(query)

        if function_id != 0:
            context = "\n".join([doc.page_content for doc in docs])
            response = process_function(function_id, context, query, docs)
        else:
            response = process_function(0, "\n".join([doc.page_content for doc in docs]), query, docs)

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
