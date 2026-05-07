from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_provider import get_llm

llm = get_llm(temperature=0)

slot_prompt = PromptTemplate.from_template("""
You are an HR audit information extraction engine.

Your task is to extract structured information from the latest HR response.

Intent:
{intent}

Latest HR Response:
{query}

Extract only information explicitly stated in the HR response.
Do not infer, assume, or use outside knowledge.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanation.
Do not wrap JSON in quotes.

Use this exact schema:
{{
  "filled_slots": {{
    "intent": "{intent}",
    "topic": "",
    "process_or_policy": "",
    "trigger": "",
    "owner": "",
    "maker": "",
    "checker_or_approver": "",
    "system_or_tracker": "",
    "documents_or_reports": "",
    "controls": "",
    "exception_handling": "",
    "employee_categories": "",
    "frequency_or_timeline": "",
    "downstream_impact": ""
  }},
  "missing_slots": [],
  "confidence": 0.0
}}

Slot definitions:
- topic: main HR area being discussed
- process_or_policy: HR process, policy, program, or initiative mentioned
- trigger: what starts the process
- owner: team or person accountable
- maker: person/team performing the activity
- checker_or_approver: person/team reviewing or approving
- system_or_tracker: HRMS, payroll system, attendance system, tracker, portal, or tool
- documents_or_reports: forms, checklists, reports, registers, approvals, letters
- controls: checks, approvals, validations, monitoring, reconciliations
- exception_handling: escalation, grievance, deviation, correction, manual override
- employee_categories: permanent, contract, trainee, apprentice, third-party, etc.
- frequency_or_timeline: daily, monthly, annual, during onboarding, during exit, etc.
- downstream_impact: payroll, access, employee master, attendance, compliance, F&F, etc.

Rules:
- If a slot is answered, fill it with a concise phrase.
- If a slot is not answered, keep it as an empty string.
- Add every empty slot name to missing_slots.
- confidence must be between 0 and 1.
- confidence should be high only when the HR response is specific and process-level.
- If the HR response is generic, confidence should be below 0.6.

Example:
HR Response:
"We use HRMS for employee master updates. HR Ops initiates the change and the HR manager approves it."

Output:
{{
  "filled_slots": {{
    "intent": "Employee Master Data",
    "topic": "employee master updates",
    "process_or_policy": "employee master data change",
    "trigger": "",
    "owner": "HR Ops",
    "maker": "HR Ops",
    "checker_or_approver": "HR manager",
    "system_or_tracker": "HRMS",
    "documents_or_reports": "",
    "controls": "approval by HR manager",
    "exception_handling": "",
    "employee_categories": "",
    "frequency_or_timeline": "",
    "downstream_impact": ""
  }},
  "missing_slots": [
    "trigger",
    "documents_or_reports",
    "exception_handling",
    "employee_categories",
    "frequency_or_timeline",
    "downstream_impact"
  ],
  "confidence": 0.82
}}

Now extract from the given HR response.
""")

slot_chain = slot_prompt | llm | StrOutputParser()