
import streamlit as st
from google import genai

st.set_page_config(
    page_title="P Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .stApp {
        background: #0e1117;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    .hero {
        text-align: center;
        padding: 1.5rem 0 2rem 0;
    }

    .hero-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .hero h1 {
        font-size: 2.5rem;
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #9ca3af;
        font-size: 1rem;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #292e39;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    [data-testid="stChatInput"] {
        border-radius: 16px;
    }

    [data-testid="stSidebar"] {
        background: #121620;
    }

    .welcome-card {
        border: 1px solid #292e39;
        border-radius: 16px;
        padding: 1.2rem;
        background: #151a24;
        margin: 1rem 0;
    }

    .small-note {
        color: #9ca3af;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 P Chatbot")
    st.caption("Your personal AI assistant")
    st.divider()

    st.markdown("### What can I help with?")
    st.markdown(
        "- 📚 Learn new concepts\n"
        "- 💻 Understand code\n"
        "- ✍️ Write and improve text\n"
        "- 💡 Brainstorm ideas"
    )

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        '<p class="small-note">Built with Python, Streamlit '
        'and Google Gemini.</p>',
        unsafe_allow_html=True,
    )

# API configuration
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "API key is missing. Configure GEMINI_API_KEY "
        "in your local secrets.toml or Streamlit Cloud secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# Choose a model available to your account
MODEL = "gemini-3.5-flash-lite"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="hero">
    <div class="hero-icon">🤖</div>
    <h1>P Chatbot</h1>
    <p>Your AI-powered assistant. Ask anything to get started.</p>
</div>
""", unsafe_allow_html=True)

# Welcome suggestions
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>👋 Welcome!</h3>
        <p>I'm here to help you learn, solve problems,
        write code, and explore new ideas.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    if col1.button(
        "📘 Explain a concept",
        use_container_width=True
    ):
        st.session_state.pending_prompt = (
            "Explain machine learning in simple words."
        )
        st.rerun()

    if col2.button(
        "💻 Help with Python",
        use_container_width=True
    ):
        st.session_state.pending_prompt = (
            "Teach me Python with a simple example."
        )
        st.rerun()

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept typed or suggested prompt
prompt = st.chat_input("Message P Chatbot...")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {
            "role": (
                "model"
                if message["role"] == "assistant"
                else "user"
            ),
            "parts": [{"text": message["content"]}],
        }
        for message in st.session_state.messages
        if message["role"] in ("user", "assistant")
    ]

    try:
        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model=MODEL,
                contents=history,
            )

            reply = response.text

            if not reply:
                reply = "I couldn't generate a text response. Please try again."

        # Create the assistant bubble only after a response exists
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
        })

        st.rerun()

    except Exception as error:
        # No empty assistant bubble is created on failure
        with st.chat_message("assistant"):
            st.warning(
                "I couldn't reach the AI service. "
                "Your message is still visible above. "
                "Please check API access and try again."
            )

        st.caption(
            "Technical details: "
            + str(error)
        )
