import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq

# Page config
st.set_page_config(
    page_icon="🤖",
    page_title="AI ChatBot Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    .stTextInput > div > div > input {
        font-size: 16px !important;
        padding: 12px !important;
    }
    .stButton > button {
        width: 100%;
        font-size: 16px;
        padding: 12px;
        -webkit-tap-highlight-color: transparent;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
        min-height: 100px;
    }
    .stApp {
        background: #000000 !important;
        color: white !important;
    }
    .title {
        background: #E62727;
        font-size: 15px;
        font-weight: bold;
        padding: 3vmin;
        border-radius: 1vmin;
        color: #DCDCDC;
        text-align: center;
        margin-bottom: 20px;
    }
    .para {
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }
    .assistant-bubble {
        background: #F0F0F0;
        color: #333333;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        text-align: left;
        float: left;
        clear: both;
        border-bottom-left-radius: 5px;
    }
    .user-bubble {
        background: #2C3E50;
        color: #FFFFFF;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        text-align: left;
        float: right;
        clear: both;
        border-bottom-right-radius: 5px;
    }
    .chat-container {
        overflow: hidden;
        margin-bottom: 15px;
    }
    .role-label {
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 0.8em;
        opacity: 0.8;
    }
    @media (max-width: 768px) {
        .assistant-bubble, .user-bubble {
            max-width: 85%;
            padding: 10px 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Groq client setup
@st.cache_resource
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found. Please set it in Streamlit secrets or .env file.")
        return None
    return Groq(api_key=api_key)

client = get_groq_client()

# Title and intro
st.markdown('<p class="title">AI Chat Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="para">Welcome to your personal AI assistant! I can help with coding, writing, analysis, and much more.</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("SETTINGS")

    model_options = {
        "🚀 Fast (8B)": "llama-3.1-8b-instant",
        "💪 Powerful (70B)": "llama-3.1-70b-versatile",
        "🔬 Balanced (3B)": "llama-3.2-3b-preview"
    }

    selected_model = st.selectbox("Choose AI Model:", list(model_options.keys()), index=0)
    model_name = model_options[selected_model]

    temperature_slider = st.slider("Creativity Level:", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Response Length:", 100, 2000, 1024)

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("- Ask coding questions\n- Request explanations\n- Get creative ideas!\n- Analyze problems\n- Learn new concepts")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Hi! I'm your AI assistant. How can I help you today?"
            }]
            st.rerun()
    with col2:
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            chat_text = "AI Chat History:\n\n"
            for msg in st.session_state.messages:
                chat_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
            st.download_button("📩 Export", chat_text, file_name="ai_chat_history.txt", mime="text/plain", use_container_width=True)

    st.markdown("---")
    st.markdown("Built with 💖 using Streamlit + Groq")

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! I'm your AI assistant. How can I help you today?"
    }]

# Display messages
st.markdown("---")
for message in st.session_state.messages:
    role_class = "assistant-bubble" if message['role'] == "assistant" else "user-bubble"
    role_label = "ASSISTANT" if message['role'] == "assistant" else "USER"
    st.markdown(f"""
        <div class="chat-container">
            <div class="{role_class}">
                <div class="role-label">{role_label}:</div>
                {message['content']}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat input
st.markdown("---")
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown(f"""
    <div class="chat-container">
        <div class="user-bubble">
            <div class="role-label">USER:</div>
            {prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)

    message_placeholder = st.empty()
    full_response = ""

    message_placeholder.markdown("""
    <div class="chat-container">
        <div class="assistant-bubble">
            <div class="role-label">ASSISTANT:</div>
            <em>Thinking...</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        if client is None:
            raise ValueError("Groq client not initialized.")

        response = client.chat.completions.create(
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            model=model_name,
            temperature=temperature_slider,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_response += delta.content
                message_placeholder.markdown(f"""
                <div class="chat-container">
                    <div class="assistant-bubble">
                        <div class="role-label">ASSISTANT:</div>
                        {full_response}▌
                    </div>
                </div>
                """, unsafe_allow_html=True)

        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT:</div>
                {full_response}
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
        full_response = "Sorry, I encountered an error. Please try again."
        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT:</div>
                {full_response}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Your personal AI assistant • Powered by Groq</p>
</div>
""", unsafe_allow_html=True)
