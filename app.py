import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables for local development
load_dotenv()

# Custom CSS for mobile responsiveness and chat bubbles
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    .main > div {
        max-width: 100%;
        padding: 1rem;
    }
    
    .stTextInput > div > div > input {
        font-size: 16px !important;
        padding: 12px !important;
        border-radius: 10px !important;
    }
    
    .stButton > button {
        width: 100%;
        font-size: 16px;
        padding: 12px;
        border-radius: 10px;
        background-color: #4A6FA5;
        color: white;
        border: none;
    }
    
    .assistant-bubble {
        background: #F0F0F0;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        word-wrap: break-word;
        text-align: left;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
        color: #333333;
    }
    
    .user-bubble {
        background: #4A6FA5;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        word-wrap: break-word;
        text-align: left;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
        margin-left: auto;
    }
    
    .chat-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }
    
    .timestamp {
        font-size: 0.8em;
        color: #666;
        margin-top: 4px;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .assistant-bubble, .user-bubble {
            max-width: 90%;
            padding: 10px 14px;
        }
        
        .stTextInput > div > div > input {
            font-size: 16px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

def get_api_key():
    """Safely get API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for deployment)
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        try:
            # Fall back to environment variables (for local development)
            return os.getenv("GROQ_API_KEY")
        except:
            return None

def initialize_groq_client():
    """Initialize Groq client with error handling"""
    try:
        api_key = get_api_key()
        if not api_key:
            st.error("🔑 API Key not found. Please set GROQ_API_KEY in your secrets or .env file.")
            return None
        
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Error initializing Groq client: {e}")
        return None

def chat_with_groq(client, message, model="mixtral-8x7b-32768"):
    """Send message to Groq API and return response"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": message}],
            model=model,
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "groq_client" not in st.session_state:
        st.session_state.groq_client = initialize_groq_client()
    
    # Header
    st.title("🤖 AI Chat Assistant")
    st.markdown("---")
    
    # Model selection
    col1, col2 = st.columns([3, 1])
    with col2:
        model = st.selectbox(
            "Model",
            ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
            index=0
        )
    
    # Chat container
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">{message["content"]}</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="assistant-bubble">{message["content"]}</div>', 
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            key="user_input",
            placeholder="Ask me anything...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Handle user input
    if (user_input and send_button) or (user_input and st.session_state.get("enter_pressed", False)):
        if st.session_state.groq_client:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("🤔 Thinking..."):
                response = chat_with_groq(st.session_state.groq_client, user_input, model)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update the chat display
            st.rerun()
        else:
            st.error("❌ Chat client not initialized. Please check your API key.")
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # Sidebar with info
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This AI assistant uses Groq's ultra-fast inference engine.
        
        **Features:**
        - Multiple model support
        - Mobile-responsive design
        - Real-time chat
        - Secure API key handling
        
        **Models:**
        - Mixtral-8x7b: Best overall
        - Llama2-70b: Powerful reasoning
        - Gemma-7b: Fast & efficient
        """)
        
        st.markdown("---")
        st.markdown("💡 **Tip:** Keep messages clear and concise for best results.")
        
        # API status
        st.markdown("---")
        if st.session_state.groq_client:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Not Connected")

if __name__ == "__main__":
    main()
