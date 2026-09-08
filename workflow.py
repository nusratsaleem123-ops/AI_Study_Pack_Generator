import json
from prompt import PLANNING_PROMPT, CONTENT_PROMPT, ASSESSMENT_PROMPT, REVIEW_PROMPT, REFINEMENT_PROMPT

def run_stage(template, context, ai_call):
    prompt = template.replace(
        "{context}",
        json.dumps(context, ensure_ascii=False, indent=2)
    )
    return ai_call(prompt)

def run_workflow(user_input, ai_call, progress=None, status=None):
    context = {"user_input": user_input}
    stages = [
        ("1️⃣ Planning", PLANNING_PROMPT, "plan", 20),
        ("2️⃣ Content Generation", CONTENT_PROMPT, "content", 40),
        ("3️⃣ Assessment", ASSESSMENT_PROMPT, "assessment", 60),
        ("4️⃣ Review", REVIEW_PROMPT, "review", 80),
        ("5️⃣ Refinement", REFINEMENT_PROMPT, "final_pack", 100),
    ]
    for name, template, key, pct in stages:
        if status: status.info(name + "...")
        context[key] = run_stage(template, context, ai_call)
        if progress: progress.progress(pct)
    return context
