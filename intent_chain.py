from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_provider import get_llm

llm = get_llm(temperature=0)

intent_prompt = PromptTemplate.from_template("""
Classify the HR intent from the following conversation.

Conversation History:
{history}

Latest HR Response:
{query}

Respond with ONLY the intent name.
""")

intent_chain = intent_prompt | llm | StrOutputParser()
