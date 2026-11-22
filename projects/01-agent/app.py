
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent, SYSTEM_PROMPT

# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="NEXUS AI | Intelligent Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. PROFESSIONAL DARK UI
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080f1e;
    --panel: #111d31;
    --panel2: #17263d;
    --border: #293c58;
    --white: #ffffff;
    --muted: #c2cde0;
    --blue: #60a5fa;
    --purple: #a78bfa;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #080f1e, #101c32 55%, #0b1425);
    color: var(--white) !important;
}

/* Make normal text readable */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
.stText,
.stCaption,
label {
    color: var(--muted) !important;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] strong {
    color: var(--white) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d182a;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--white) !important;
}

/* Main layout */
.main .block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hero */
.hero {
    padding: 32px;
    border: 1px solid #344b6d;
    border-radius: 22px;
    background: linear-gradient(120deg, #172d4c, #24264a, #17243c);
    margin-bottom: 25px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
}

.hero h1 {
    color: #ffffff !important;
    font-size: 36px;
    font-weight: 800;
    margin: 5px 0;
}

.hero p {
    color: #d4deef !important;
    font-size: 14px;
}

.tag {
    display: inline-block;
    background: #263f63;
    color: #bfdbfe !important;
    border: 1px solid #5276a5;
    padding: 6px 12px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
}

/* Cards */
.metric-card, .tool-card, .info-card {
    background: linear-gradient(145deg, #17263d, #111d30);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 19px;
    min-height: 105px;
    transition: .2s ease;
}

.metric-card:hover, .tool-card:hover {
    border-color: var(--blue);
    transform: translateY(-2px);
}

.metric-title {
    color: #bdcbe0 !important;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .7px;
}

.metric-value {
    color: #ffffff !important;
    font-size: 23px;
    font-weight: 800;
    margin-top: 9px;
}

.tool-card strong {
    color: #ffffff !important;
    font-size: 15px;
}

.tool-card p {
    color: #c2cde0 !important;
    font-size: 12px;
    margin-top: 8px;
}

.section-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 700;
    margin: 25px 0 14px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #17263d;
    border: 1px solid #304663;
    border-radius: 16px;
    padding: 15px;
    margin-bottom: 13px;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #ffffff !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #142238 !important;
    border: 1px solid #49658a !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #bdcbe0 !important;
}

/* Other input fields */
input, textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-baseweb="select"] > div {
    background: #17263d !important;
    color: #ffffff !important;
    border-color: #405878 !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(110deg, #2563eb, #6845c5);
    color: #ffffff !important;
    border: 1px solid #6689d2;
    border-radius: 11px;
    font-weight: 700;
    transition: .2s ease;
}

.stButton button p {
    color: #ffffff !important;
}

.stButton button:hover {
    background: linear-gradient(110deg, #3b82f6, #805ad5);
    border-color: #a5c8ff;
    transform: translateY(-1px);
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #d5e0f2 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
}

/* Dividers and footer */
hr {
    border-color: #2b3d57 !important;
}

.footer {
    text-align: center;
    color: #b4c2d8 !important;
    font-size: 12px;
    padding: 30px 10px;
}

/* Mobile */
@media (max-width: 768px) {
    .hero { padding: 22px; }
    .hero h1 { font-size: 27px; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. API CONNECTION
# =====================================================

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL", "openrouter/free")

if not api_key:
    st.error("API key missing. Please configure your .env file.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url=base_url if base_url else None
)

# =====================================================
# 4. SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

if "request_count" not in st.session_state:
    st.session_state.request_count = 0

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "show_details" not in st.session_state:
    st.session_state.show_details = True

# =====================================================
# 5. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("# 🤖 NEXUS AI")
    st.caption("INTELLIGENT AGENT PLATFORM")

    st.divider()

    if st.button("＋ New Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

    st.markdown("### ⚙️ Agent Configuration")

    st.success("● API Connected")

    st.markdown("**Active Model**")
    st.code(model)

    st.markdown("**Agent Status**")
    st.markdown("🟢 Ready to receive requests")

    st.divider()

    st.markdown("### 🧰 Available Tools")

    st.markdown("""
    - 🧮 Calculator
    - 🕒 Date & Time
    - 📄 File Reader
    - 📁 File Explorer
    """)

    st.divider()

    st.markdown("### 📊 Session Analytics")

    user_messages = sum(
        1 for message in st.session_state.messages
        if message["role"] == "user"
    )

    st.metric("User Messages", user_messages)
    st.metric("Successful Requests", st.session_state.request_count)

    st.divider()

    st.session_state.show_details = st.toggle(
        "Show tool information",
        value=st.session_state.show_details
    )

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

    st.caption("Built with Python • Streamlit • OpenRouter")

# =====================================================
# 6. HERO SECTION
# =====================================================

st.markdown("""
<div class="hero">
    <div class="tag">✦ INTELLIGENT AI PLATFORM</div>
    <h1>NEXUS AI Assistant</h1>
    <p>
        Your personal AI agent for intelligent conversations,
        calculations, file operations and productivity.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 7. DASHBOARD METRICS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">AGENT STATUS</div>
        <div class="metric-value">🟢 Online</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">ACTIVE MODEL</div>
        <div class="metric-value">Connected</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">AVAILABLE TOOLS</div>
        <div class="metric-value">04 Tools</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 8. INTERACTIVE NAVIGATION
# =====================================================

chat_tab, tools_tab, analytics_tab = st.tabs([
    "💬 AI Chat",
    "⚡ Capabilities",
    "📊 Analytics"
])

# =====================================================
# 9. CHAT TAB
# =====================================================

with chat_tab:

    st.markdown(
        '<div class="section-title">💬 AI Conversation</div>',
        unsafe_allow_html=True
    )

    st.caption("Ask NEXUS AI anything. Select a suggested prompt or type your own.")

    # Quick prompts
    st.markdown("**Try a quick prompt**")

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button("🧮 Calculate", use_container_width=True):
            st.session_state.pending_prompt = "What is (1450 * 3) / 7?"
            st.rerun()

    with q2:
        if st.button("📁 List project files", use_container_width=True):
            st.session_state.pending_prompt = "List the files in my project."
            st.rerun()

    with q3:
        if st.button("🕒 Current time", use_container_width=True):
            st.session_state.pending_prompt = "What is the current date and time?"
            st.rerun()

    st.divider()

    # Display conversation history
    for message in st.session_state.messages:
        if message["role"] in ("user", "assistant") and message.get("content"):
            with st.chat_message(
                message["role"],
                avatar="👤" if message["role"] == "user" else "🤖"
            ):
                st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Message NEXUS AI...")

    if st.session_state.pending_prompt:
        user_input = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):

            with st.spinner("NEXUS AI is thinking..."):

                try:
                    answer = run_agent(
                        client,
                        model,
                        st.session_state.messages
                    )

                    st.markdown(answer)

                    # Save answer if run_agent did not already add it
                    if (
                        not st.session_state.messages
                        or st.session_state.messages[-1]["role"] != "assistant"
                    ):
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    st.session_state.request_count += 1

                except Exception as error:
                    st.error(f"Agent Error: {error}")

# =====================================================
# 10. CAPABILITIES TAB
# =====================================================

with tools_tab:

    st.markdown(
        '<div class="section-title">⚡ Agent Capabilities</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="tool-card">
            <strong>🧮 Calculator</strong>
            <p>Perform mathematical calculations using the agent's calculator tool.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tool-card">
            <strong>📄 File Reader</strong>
            <p>Read supported text files from the project repository.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="tool-card">
            <strong>🕒 Date & Time</strong>
            <p>Get current date and time information.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tool-card">
            <strong>📁 File Explorer</strong>
            <p>Explore available files and folders in the project.</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.show_details:
        with st.expander("How does the agent work?"):
            st.write(
                "NEXUS AI receives your message, decides whether a tool is "
                "needed, executes the available tool and returns a response."
            )

# =====================================================
# 11. ANALYTICS TAB
# =====================================================

with analytics_tab:

    st.markdown(
        '<div class="section-title">📊 Session Analytics</div>',
        unsafe_allow_html=True
    )

    total_messages = sum(
        1 for message in st.session_state.messages
        if message["role"] == "user"
    )

    a1, a2, a3 = st.columns(3)

    a1.metric("User Messages", total_messages)
    a2.metric("Successful Requests", st.session_state.request_count)
    a3.metric("Available Tools", 4)

    st.divider()

    st.markdown("### Conversation Overview")

    if total_messages:
        st.success(f"You have sent {total_messages} message(s) in this session.")
    else:
        st.info("No messages yet. Start a conversation to see your activity.")

    if st.button("Refresh Analytics", use_container_width=False):
        st.rerun()

# =====================================================
# 12. FOOTER
# =====================================================

st.markdown("""
<div class="footer">
    <strong>NEXUS AI © 2026</strong><br>
    Intelligent Tool-Calling Agent<br>
    Powered by Python, Streamlit and OpenRouter
</div>
""", unsafe_allow_html=True)
