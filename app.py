import os, json, time
import streamlit as st
from groq import Groq
from workflow import run_workflow

st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

def call_groq_json(prompt, retries=2):
    key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    if not key: raise ValueError("Groq API key is missing.")
    client = Groq(api_key=key)
    last_error = None
    for attempt in range(retries + 1):
        try:
            r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[
                {"role":"system","content":"You are an educational AI agent. Return valid JSON only."},
                {"role":"user","content":prompt}], temperature=0.3, max_tokens=6000)
            text = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
            return json.loads(text)
        except Exception as e:
            last_error = e
            if attempt < retries: time.sleep(1.5)
    raise RuntimeError(f"AI stage failed after retries: {last_error}")

def render_pack(p):
    st.markdown(f"# 📚 {p.get('title','AI Study Pack')}")
    st.markdown(f"### Overview\n{p.get('overview','')}")
    with st.expander("🎯 Learning Objectives", True):
        for x in p.get("learning_objectives",[]): st.write("•",x)
    with st.expander("📖 Study Notes", True):
        for x in p.get("study_notes",[]):
            st.markdown(f"**{x.get('heading','')}**"); st.write(x.get("explanation",""))
            if x.get("example"): st.info("Example: " + x["example"])
    with st.expander("🔑 Key Concepts", True):
        for x in p.get("key_concepts",[]): st.markdown(f"**{x.get('term','')}** — {x.get('definition','')}")
    with st.expander("🧠 Flashcards"):
        for i,x in enumerate(p.get("flashcards",[]),1): st.markdown(f"**{i}. {x.get('question','')}**"); st.write(x.get("answer",""))
    with st.expander("❓ MCQ Quiz"):
        for i,x in enumerate(p.get("mcqs",[]),1):
            st.markdown(f"**{i}. {x.get('question','')}**")
            for o in x.get("options",[]): st.write(o)
            st.success("Answer: " + x.get("correct_answer","")); st.caption(x.get("explanation",""))
    with st.expander("✍️ Short Questions"):
        for x in p.get("short_questions",[]): st.markdown(f"**{x.get('question','')}**"); st.write("Answer points:", ", ".join(x.get("answer_points",[])))
    with st.expander("📅 Study Plan"):
        for x in p.get("study_plan",[]): st.write("•",x)
    with st.expander("💡 Exam Tips"):
        for x in p.get("exam_tips",[]): st.write("•",x)

st.title("📚 AI Study Pack Generator")
st.caption("Planning → Content → Assessment → Review → Refinement")
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state["groq_api_key"] = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY",""), type="password")
c1,c2=st.columns(2)
with c1:
    subject=st.text_input("📚 Subject","Biology"); topic=st.text_input("📖 Topic","Photosynthesis"); level=st.selectbox("🎓 Student Level",["Beginner","Intermediate","Advanced"])
with c2:
    study_time=st.selectbox("⏱️ Study Time",["30 minutes","1 hour","2 hours","1 day","1 week"]); goal=st.selectbox("🎯 Goal",["Exam preparation","Concept understanding","Quick revision","Practice"])
if st.button("🚀 Generate Study Pack", type="primary", use_container_width=True):
    if not subject.strip() or not topic.strip(): st.warning("Please enter subject and topic.")
    elif not (st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")): st.warning("Please enter your Groq API key.")
    else:
        user_input={"subject":subject.strip(),"topic":topic.strip(),"level":level,"study_time":study_time,"goal":goal}
        progress=st.progress(0); status=st.empty()
        try: st.session_state["context"]=run_workflow(user_input,call_groq_json,progress,status)
        except Exception as e: status.error("❌ Workflow stopped safely."); st.error(str(e))
if "context" in st.session_state:
    ctx=st.session_state["context"]; st.divider(); st.subheader("🔄 Workflow Completed")
    cols=st.columns(5)
    for col,name in zip(cols,["Planning","Content","Assessment","Review","Refinement"]): col.success("✅ "+name)
    st.divider(); render_pack(ctx["final_pack"])
    st.download_button("⬇️ Download Study Pack JSON",json.dumps(ctx["final_pack"],ensure_ascii=False,indent=2),"study_pack.json","application/json")
