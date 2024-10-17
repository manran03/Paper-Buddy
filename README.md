# Research Paper Question Answering App

## Overview

This Flask-based application allows users to upload research papers in PDF format and ask questions about their content. The app processes the PDF, extracts its text, and utilizes Google's Generative AI models to answer questions, summarize, and rate the paper based on different criteria.

![image](https://github.com/user-attachments/assets/09608302-f21d-4e08-b655-4d1496bfc292)

![image](https://github.com/user-attachments/assets/08a5c441-c6a6-495b-8c78-b572ce817883)

![image](https://github.com/user-attachments/assets/4db7b331-3fa8-4e47-9174-06faccb6530e)



## Features

- **PDF Upload**: Users can upload research papers in PDF format via a base64 string.
- **Text Extraction**: Extracts text from the uploaded PDF for processing.
- **Question Answering**: Answers user questions based on the paper's content.
- **Paper Analysis**:
  - Rates the quality of the paper.
  - Extracts important points.
  - Rates the readability of the paper.
- **Vector Store for Document Retrieval**: Uses FAISS for text chunk storage and similarity search for efficient retrieval of information.
- **Flask API**: The app is built with Flask and provides an API for interaction.
- **CORS Enabled**: Cross-Origin Resource Sharing is enabled for seamless integration with other frontends.

## Tech Stack

- **Flask**: Web framework for handling API requests.
- **PyPDF2**: For reading and extracting text from PDFs.
- **Langchain**: Handles text splitting, embedding generation, and question-answering logic.
- **Google Generative AI (Gemini models)**: Provides embeddings and models for text processing, question answering, and paper rating.
- **FAISS**: A vector search library for document similarity searches.
- **Flask-CORS**: Allows cross-origin requests.
- **Dotenv**: Loads environment variables from a `.env` file.

## Requirements

- Python 3.7+
- A Google API key with access to Google's Generative AI models.
- A `.env` file with the following key:
  ```plaintext
  GOOGLE_API_KEY=your_google_api_key
## API Endpoints
/process_pdf (POST)
This endpoint accepts a research paper in base64-encoded format and a user query, processes the PDF, and provides an appropriate response.

Parameters:
pdf_base64: Base64-encoded string of the research paper PDF.
query: User's query or prompt regarding the paper.
Response:
response: A detailed answer to the user's query, or a summary/rating of the paper based on the prompt.

## Usage Flow

Upload PDF: The user uploads a research paper in PDF format (base64 encoded).
Ask a Question: The user sends a query related to the paper (e.g., "Summarize the key points").
Receive Answer: The app processes the PDF, analyzes the content, and provides an answer or rating.

## Error Handling

The API will return a 400 error if either the PDF or query is missing.
If any processing error occurs, a 500 error is returned with the error message.

## License

This project is licensed under the MIT License.
