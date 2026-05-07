# HR_Audit_Copilot_backend
🧠 HR Audit Copilot (RAG + Agent + Tooling)
An AI-powered HR audit assistant that simulates an interviewer asking intelligent, context-aware questions based on HR policy documents.

🚀 Overview
This project implements a Retrieval-Augmented Generation (RAG) system with an agent-based architecture that:

Ingests HR policy documents (PDF/DOCX)
Builds a vector database using embeddings
Generates structured HR interview questions
Extracts intent and slots from HR responses
Uses Google Search as a fallback tool when RAG is insufficient
🏗️ Architecture
User (HR Response)
        ↓
Intent Detection (LLM)
        ↓
Slot Extraction (LLM → JSON)
        ↓
RAG Retrieval (Chroma DB)
        ↓
Agent Decision
   ├── If sufficient → Answer from RAG
   └── If insufficient → Google Search Tool
        ↓
LLM Answer Generation
        ↓
Next Question Generation
🧩 Components
1. 📄 Document Ingestion
Upload HR policy files (PDF, DOCX)
Chunking + embedding
Stored in Chroma Vector DB
File: vector_store.py

2. 🔍 RAG Retrieval
Retrieves relevant chunks based on query
Uses embeddings similarity search
File: rag_tool.py

3. 🧠 LLM Integration
Custom Azure OpenAI wrapper
Supports both embeddings + chat
File: llm_provider.py

4. 🎯 Intent Detection
Classifies HR response into categories like:

onboarding
payroll
employee engagement
File: intent_chain.py

5. 📦 Slot Extraction
Extracts structured audit data:

{
  "filled_slots": {
    "process_or_policy": "",
    "owner": "",
    "system_or_tracker": ""
  },
  "missing_slots": []
}
File: slot_chain.py

6. 🤖 Agent (Core Logic)
Decision-making layer:

RAG → sufficient → return answer  
RAG → insufficient → Google Search  
File: agent_chain.py

7. 🌐 Google Search Tool (Fallback)
Used when:

RAG context is weak
Question is general/public
File: google_search_tool.py

8. ❓ Question Generation
Generates next interviewer question

File: question_chain.py

9. 🌐 API Layer (FastAPI)
Endpoints:

Endpoint	Description
/api/upload-policy	Upload and index document
/api/next-question	Process HR response
File: main.py

⚙️ Setup
1. Install dependencies
pip install -r requirements.txt
2. Environment variables (.env)
LLM_PROVIDER=azure_openai

AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2024-02-01

AZURE_OPENAI_EMBEDDING_ENDPOINT=your_embedding_endpoint

GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_CX=your_search_engine_id
3. Run backend
uvicorn main:app --reload
4. Run frontend
npm install
npm run dev
🧪 Example Flow
Upload HR policy
System generates first question
HR responds
System:
Detects intent
Extracts slots
Uses RAG / Google
Generates next question
🧠 Agent Design
Current (POC)
if RAG answer is weak:
    use Google Search
Improved (Recommended)
1. Check retrieval scores
2. Validate answer quality
3. Route to tool if needed
4. Return source + confidence
📊 Output Format
{
  "next_question": "...",
  "intent": "...",
  "filled_slots": {},
  "missing_slots": [],
  "answer": "...",
  "source_used": "rag | google_search",
  "confidence": 0.87
}
🎯 Features
✅ RAG-based contextual questioning
✅ Intent classification
✅ Structured slot extraction
✅ Tool-based fallback (Google Search)
✅ Clean frontend chat UI
✅ Azure OpenAI integration
✅ Persistent vector DB

⚠️ Limitations
Google search may not help for internal policies
Slot extraction depends on prompt quality
Confidence score is heuristic (not model-based yet)
🔥 Future Improvements
Add retrieval score-based routing
Use LangChain Agents / Tool Router
Add source citations
Improve slot schema dynamically based on intent
Add multi-document support
Add evaluation metrics
📌 Key Learnings
RAG alone is not enough → need tools
Prompt design is critical for structured output
LLMs tend to generate generic questions without constraints
Backend parsing must be robust
👨‍💻 Author
Built as part of an HR Audit AI Copilot POC.
