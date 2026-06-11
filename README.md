# python-chatbot-milo
muthoot ai chatbot

Subject : Proposal for AI powered Customer Support Chatbot : Milo

I am writing to share the proposal and idea documentation for the AI Powered Chatbot : Milo , the project I am planning to implement during my internship.

Project Overview:  

The chatbot will assist customers in checking loan balances, EMI schedules, repayment dates, and handling inquiries or complaints. It will support both structured (database) and unstructured (emails, messages, FAQs) queries while ensuring secure per-user access.

Key Features:  

1. Structured Query Handling:  
   - Queries like “What is my loan balance?” or “When is my next EMI due?” will be fetched directly from the Oracle SQL database.  
2. Unstructured Query Handling:  
   - Free form questions like “Why is my loan approval delayed?” will be processed using Retrieval Augmented Generation (RAG) to provide accurate, context aware responses.  
3. Secure Access:  
   - Each customer will only be able to access their own information using JWT authentication.
  
Technical Stack:  

- Backend: Python with FastAPI and Uvicorn server  
- AI/NLP: RAG model (Hugging Face Transformers) + NLTK for text preprocessing  
- Database: Oracle SQL / SQL Plus  
- Data Handling: Pandas for Excel/CSV imports  
- Security: JWT for authentication  
- IDE: VS Code  

Workflow:  

1. User sends a query via the frontend.  
2. FastAPI receives the query.  
3. Query type is identified: structured → direct SQL query; unstructured → NLTK preprocessing → RAG generates response.  
4. Response is sent back to the user.

Advantages:  

- Provides dynamic, human like responses for complex queries.  
- Handles both structured and unstructured queries.  
- Secure per user access.  
