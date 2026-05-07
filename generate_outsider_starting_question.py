from llm_provider import get_llm


def generate_outsider_starting_question(vectordb):
    print("111111111111111111111111: entered function")

    try:
        print("222222222222222222222222: before get_llm")
        llm = get_llm()
        print("333333333333333333333333: after get_llm")
    except Exception as e:
        print("❌ get_llm failed:", e)
        raise

    docs = vectordb.similarity_search(
        query="What are the main employee-related themes in this company?",
        k=6,
    )

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
You are helping an external person prepare questions for an HR conversation.

Goal:
- Ask ONE strong opening question the person can ask HR
- The question should help understand the company culture, rules, or employee experience
- Do NOT mention policies, documents, files, or uploads
- Do NOT sound like an internal reviewer
- Do NOT ask multiple questions
- Keep it natural and conversational
Rules:
- Do NOT wrap the question in quotes
- Output plain text only
Use the following information only as background context
(not something referred to in the question):

{context}

Write the single best opening question:
"""

    try:
        print("0000000000000000000000 before llm.invoke")
        response = llm.invoke(prompt)
        print("----------------------------------DEBUG: after llm.invoke")
        print("response.content.strip()", response.content.strip())
        return response.content.strip()
    except Exception as e:
        print("❌ llm.invoke failed:", e)
        raise