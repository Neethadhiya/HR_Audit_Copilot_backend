from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from generate_outsider_starting_question import generate_outsider_starting_question

import json
import os
import shutil
import sys

from vector_store import ingest_hr_policy
from intent_chain import intent_chain
from slot_chain import slot_chain
from question_chain import question_chain
from agent_chain import run_agent
from utils import serialize_history

sys.stdout.flush()

# ─────────────────────────────────────────────
# Environment setup
# ─────────────────────────────────────────────

load_dotenv()

TEMP_DIR = os.path.abspath("temp")

# ─────────────────────────────────────────────
# FastAPI app initialization
# ─────────────────────────────────────────────

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Startup event
# ─────────────────────────────────────────────

@app.on_event("startup")
def startup():
    os.makedirs(TEMP_DIR, exist_ok=True)

    provider = os.getenv("LLM_PROVIDER")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    print("✅ FastAPI started")
    print("✅ LLM_PROVIDER:", provider)
    print("✅ Azure endpoint set:", bool(endpoint))


# ─────────────────────────────────────────────
# Upload HR Policy
# ─────────────────────────────────────────────

@app.post("/api/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if not filename.endswith(".pdf") and not filename.endswith(".docx"):
        return {
            "status": "error",
            "message": "Only PDF or DOCX files allowed"
        }

    try:
        file_path = os.path.join(TEMP_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("✅ File saved at:", file_path)

        vectordb = ingest_hr_policy(file_path)
        starting_question = generate_outsider_starting_question(vectordb)

        return {
            "status": "success",
            "message": "Policy uploaded and indexed successfully",
            "starting_question": to_text(starting_question)
        }

    except Exception as e:
        print("❌ Upload error:", e)
        return {
            "status": "error",
            "message": str(e)
        }


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def to_text(value):
    if isinstance(value, str):
        text = value.strip()
    elif hasattr(value, "content"):
        text = str(value.content).strip()
    else:
        text = str(value).strip()

    text = text.strip()

    while (
        len(text) >= 2
        and text[0] in ['"', "'", "“", "‘"]
        and text[-1] in ['"', "'", "”", "’"]
    ):
        text = text[1:-1].strip()

    return text


def parse_slots(value):
    text = to_text(value)

    try:
        data = json.loads(text)
    except Exception:
        print("⚠️ Slot JSON parse failed. Raw slot text:", text)
        return {
            "filled_slots": {"raw": text},
            "missing_slots": [],
            "confidence": 0.5
        }

    return {
        "filled_slots": data.get("filled_slots", {}),
        "missing_slots": data.get("missing_slots", []),
        "confidence": data.get("confidence", 0.5)
    }


def normalize_agent_result(agent_result):
    """
    Supports both:
    1. run_agent() returning plain string
    2. run_agent() returning dict:
       {
         "answer": "...",
         "source_used": "rag/google_search/both/none",
         "confidence": 0.7
       }
    """

    if isinstance(agent_result, dict):
        return {
            "answer": to_text(agent_result.get("answer", "")),
            "source_used": agent_result.get("source_used", "rag"),
            "confidence": agent_result.get("confidence", 0.5)
        }

    return {
        "answer": to_text(agent_result),
        "source_used": "rag",
        "confidence": 0.5
    }


# ─────────────────────────────────────────────
# RAG-based Next Question API
# ─────────────────────────────────────────────

@app.post("/api/next-question")
async def next_question(body: dict):
    history = body.get("history") or []
    transcript = body.get("transcript", "").strip()

    history_text = serialize_history(history)

    print("\n================ REQUEST =================")
    print("Transcript:", transcript)
    print("History:", history_text)

    # Intent detection
    intent_result = intent_chain.invoke({
        "history": history_text,
        "query": transcript
    })

    print("\n🧠 Intent Raw:", intent_result)
    intent = to_text(intent_result)
    print("🧠 Intent Parsed:", intent)

    # Slot extraction
    slot_result = slot_chain.invoke({
        "intent": intent,
        "query": transcript
    })

    print("\n📦 Slots Raw:", slot_result)
    slot_data = parse_slots(slot_result)

    print("📦 Filled Slots:", slot_data["filled_slots"])
    print("📦 Missing Slots:", slot_data["missing_slots"])

    # RAG / Agent answer
    agent_result = run_agent(transcript, history)
    agent_data = normalize_agent_result(agent_result)

    answer = agent_data["answer"]
    source_used = agent_data["source_used"]
    agent_confidence = agent_data["confidence"]

    print("\n📚 Agent Answer:", answer)
    print("📚 Source Used:", source_used)
    print("📚 Agent Confidence:", agent_confidence)

    # Follow-up question
    question_input = history_text + "\nHR: " + transcript

    question_result = question_chain.invoke({
        "history": question_input
    })

    print("\n❓ Question Raw:", question_result)
    question = to_text(question_result)
    print("❓ Question Parsed:", question)

    final_confidence = slot_data.get("confidence", agent_confidence)

    response = {
        "next_question": question,
        "intent": intent,
        "filled_slots": slot_data["filled_slots"],
        "missing_slots": slot_data["missing_slots"],
        "confidence": final_confidence,
        "answer": answer,
        "source_used": source_used
    }

    print("\n================ RESPONSE =================")
    print(response)

    return response