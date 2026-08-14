import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(page_title="AI Deep Research Pipeline", page_icon="🔬", layout="wide")

# ── Modern Indigo/Cyan Styling ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #e2e8f0; }
.stApp { background: #0b0f19; background-image: radial-gradient(circle at 50% 0%, rgba(6,182,212,0.12) 0%, transparent 60%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem; max-width: 1100px; }

/* Headers */
.hero { text-align: center; margin-bottom: 2rem; }
.hero h1 { font-size: 2.6rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.5rem; }
.hero span { color: #38bdf8; }
.hero p { color: #94a3b8; font-size: 1rem; }

/* Buttons & Inputs */
.stButton > button {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 14px rgba(2,132,199,0.3) !important;
}
.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }

/* Step Status */
.step-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.step-card.active { border-color: #38bdf8; background: rgba(56, 189, 248, 0.05); }
.step-card.done { border-color: #34d399; background: rgba(52, 211, 153, 0.05); }

/* Panels */
.report-panel { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 2rem; margin-top: 1rem; }
.feedback-panel { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 12px; padding: 2rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "running" not in st.session_state:
    st.session_state.running = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Autonomous <span>Deep Research</span></h1>
    <p>Multi-agent pipeline: Search, Deep-Read, Synthesize, and Critique</p>
</div>
""", unsafe_allow_html=True)

# ── Input & Stepper Layout ────────────────────────────────────────────────────
col_in, col_steps = st.columns([5, 4])

with col_in:
    topic = st.text_input("Enter Topic", placeholder="e.g. Advancements in Solid State Batteries", label_visibility="collapsed")
    run_btn = st.button("Run Research Pipeline ⚡", use_container_width=True)

with col_steps:
    r = st.session_state.results
    steps = [
        ("01", "Search Agent", "search"),
        ("02", "Reader Agent", "reader"),
        ("03", "Writer Chain", "writer"),
        ("04", "Critic Chain", "critic"),
    ]
    for num, name, key in steps:
        state = "done" if key in r else ("active" if st.session_state.running else "waiting")
        badge = "✓ Done" if state == "done" else ("● Running" if state == "active" else "Waiting")
        color = "#34d399" if state == "done" else ("#38bdf8" if state == "active" else "#64748b")
        st.markdown(f"""
        <div class="step-card {state}">
            <div><b style="color:#38bdf8;font-family:monospace;">{num}</b> <span style="font-weight:600;margin-left:8px;">{name}</span></div>
            <span style="font-size:0.75rem;font-weight:600;color:{color};">{badge}</span>
        </div>
        """, unsafe_allow_html=True)

# ── Execution Pipeline ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please provide a topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.current_topic = topic
        st.rerun()

if st.session_state.running:
    t = st.session_state.current_topic
    
    # 1. Search
    with st.spinner("🔍 Agent is searching the web..."):
        search_res = build_search_agent().invoke({"input": f"Find detailed, reliable information about: {t}"})
        st.session_state.results["search"] = search_res["output"]

    # 2. Reader
    with st.spinner("📄 Reader is scraping relevant sources..."):
        reader_res = build_reader_agent().invoke({
            "input": f"Extract the exact URL from these search results and scrape it:\n\n{st.session_state.results['search']}"
        })
        st.session_state.results["reader"] = reader_res["output"]

    # 3. Writer
    with st.spinner("✍️ Synthesizing comprehensive research report..."):
        combined = f"SEARCH:\n{st.session_state.results['search']}\n\nSCRAPED:\n{st.session_state.results['reader']}"
        st.session_state.results["writer"] = writer_chain.invoke({"topic": t, "research": combined})

    # 4. Critic
    with st.spinner("🧐 Critic is evaluating report quality..."):
        st.session_state.results["critic"] = critic_chain.invoke({"report": st.session_state.results["writer"]})

    st.session_state.running = False
    st.rerun()

# ── Output Display ────────────────────────────────────────────────────────────
res = st.session_state.results
if res:
    st.write("---")
    
    # Expanders for raw agent scratchpads
    with st.expander("🔍 Agent Search Data"):
        st.write(res.get("search", ""))
    with st.expander("📄 Scraped Source Content"):
        st.write(res.get("reader", ""))

    # Final Formatted Output
    if "writer" in res:
        st.markdown('<div class="report-panel"><h3 style="color:#38bdf8;margin-top:0;">📝 Research Report</h3>', unsafe_allow_html=True)
        st.markdown(res["writer"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.download_button(
            label="Download Report (.md)",
            data=res["writer"],
            file_name=f"report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )

    if "critic" in res:
        st.markdown('<div class="feedback-panel"><h3 style="color:#34d399;margin-top:0;">🧐 Peer Review & Critique</h3>', unsafe_allow_html=True)
        st.markdown(res["critic"])
        st.markdown('</div>', unsafe_allow_html=True)