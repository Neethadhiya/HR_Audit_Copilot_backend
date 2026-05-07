from langchain_core.prompts import PromptTemplate
from llm_provider import get_llm

llm = get_llm()

question_prompt = PromptTemplate.from_template("""
You are an HR interviewer agent.
Generate ONE follow-up question.

Rules:
- Do NOT wrap the question in quotes
- Output plain text only
- Keep it natural and conversational
Ask the NEXT BEST HR POLICY QUESTION.
Conversation:
{history}

Question:

""")

question_chain = question_prompt | llm