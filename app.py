import streamlit as st

st.set_page_config(
    page_icon="🤖",
    page_title="AI ChatBot Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

from dotenv import load_dotenv
import os
from groq import Groq

# Fixed CSS with proper syntax
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
    
    /* Fixed CSS syntax - added ! before important */
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
        min-height: 100px;
    }
    
    /* Main app styling */
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
    
    /* Chat bubble styles */
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
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .assistant-bubble, .user-bubble {
            max-width: 85%;
            padding: 10px 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()

@st.cache_resource
def get_groq_client():
    try:
        # Try Streamlit secrets first (for deployment)
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("✅ Using Streamlit secrets")
    except (KeyError, FileNotFoundError):
        try:
            # Fall back to environment variables (for local development)
            api_key = os.getenv("GROQ_API_KEY")
            st.success("✅ Using environment variables")
        except:
            st.error("❌ GROQ_API_KEY not found. Please set it in Streamlit secrets or .env file")
            return None
    
    if not api_key:
        st.error("❌ GROQ_API_KEY is empty. Please check your configuration.")
        return None
        
    return Groq(api_key=api_key)

client = get_groq_client()

# App title and description
st.markdown("""
<p class="title">AI Chat Assistant</p>
""", unsafe_allow_html=True)

st.markdown("""
<p class="para">Welcome to your personal AI assistant! 
I can help with coding, writing, analysis, and much more.</p>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.title("SETTINGS")
    
    model_options = {
        "🚀 Fast (8B)": "llama-3.1-8b-instant",
        "💪 Powerful (70B)": "llama-3.1-70b-versatile", 
        "🔬 Balanced (3B)": "llama-3.2-3b-preview"
    }
    
    selected_model = st.selectbox(
        "Choose AI Model:",
        options=list(model_options.keys()),
        index=0
    )
    model_name = model_options[selected_model]
    
    temperature_slider = st.slider(
        "Creativity Level:",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="Lower = more focused, Higher = more creative"        
    )
    
    max_tokens = st.slider(
        "Response Length:",
        min_value=100,
        max_value=2000,
        value=1024,
        help="Maximum length of AI response"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Ask coding questions
    - Request explanations  
    - Get creative ideas!
    - Analyze problems
    - Learn new concepts  
    """)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hi! I'm your AI assistant. How can I help you today?"
                }
            ]
            st.rerun()
    
    with col2:
        # Export chat functionality
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            chat_text = "AI Chat History:\n\n"
            for msg in st.session_state.messages:
                chat_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
            st.download_button(
                "📩 Export",
                chat_text,
                file_name="ai_chat_history.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown("---")
    st.markdown("Built with 💖 using Streamlit + Groq")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm your AI assistant. How can I help you today?"
        }
    ]

# Display chat messages
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

# Chat input at the bottom
st.markdown("---")
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    st.markdown(f"""
    <div class="chat-container">
        <div class="user-bubble">
            <div class="role-label">USER:</div>
            {prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display assistant response area
    message_placeholder = st.empty()
    full_response = ""
    
    # Show "Thinking..." initially
    message_placeholder.markdown("""
    <div class="chat-container">
        <div class="assistant-bubble">
            <div class="role-label">ASSISTANT:</div>
            <em>Thinking...</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Check if client is initialized
        if client is None:
            raise Exception("Groq client not initialized. Please check your API key.")
            
        response = client.chat.completions.create(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            model=model_name,
            temperature=temperature_slider,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                # Update with typing cursor
                message_placeholder.markdown(f"""
                <div class="chat-container">
                    <div class="assistant-bubble">
                        <div class="role-label">ASSISTANT:</div>
                        {full_response}▌
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Final display without cursor
        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT:</div>
                {full_response}
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        full_response = "Sorry, I encountered an error. Please try again."
        
        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT:</div>
                {full_response}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Your personal AI assistant • Powered by Groq</p>
</div>
""", unsafe_allow_html=True)
