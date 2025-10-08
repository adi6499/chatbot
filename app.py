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

load_dotenv()


@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_ENV"))

client = get_groq_client()


#setting up the website


st.markdown("""
<style>

    .stApp {
        background:#000000;
        color: white;
    }
    .title{
    background:#E62727;
    font-size:15px;
    font-weight:bold;
    padding:3vmin;
    border-radius:1vmin;
    color:#DCDCDC;
    }
    body{
        background:#1B3C53;
    }
</style>
""",unsafe_allow_html=True)

#App title and description
st.markdown(f"""
<p class="title">AI Chat Assistant</p>
""",unsafe_allow_html=True)


st.markdown(f"""
<p class="para">Welcome to your personal AI assistant!
I can help with coding, writing, analysis, and much more.</p>
""",unsafe_allow_html=True)


#sidebar configuration
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
        value=1042,
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
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages=[
            {
                "role":"assistant",
                "content":"Hi! I'm your AI assistant. How can I help you today?"
            }
        ]
        
        st.rerun()
    
    if st.button("🗃️ Export Chat"):
        if "messages" in st.session_state:
            chat_text = "AI Chat Histort:\n\n"
            for msg in st.session_state.messages:
                chat_text+=f"{msg['role'].upper()}:{msg['content']}\n\n"
                
            st.download_button(
                "📩 Download Chat",
                chat_text,
                file_name="ai_chat_history.txt",
                mime="text/plain"
            )
    
    st.markdown("---")
    st.markdown("Built with 💖 using Streamlit + Groq")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"assistant",
            "content":"Hi! I'm your AI assistant. How can I help you today?"
        }
    ]

st.markdown("""
<style>
  .assistant-bubble {
       background: #F0F0F0;  /* Light gray */
    color: #333333;
        padding: 12px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        text-align: left;
        float: left;
        color:black;
    }
    .user-bubble {
          background: #2C3E50;  /* Dark blue-gray */
    color: #FFFFFF; 
        padding: 12px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        text-align: right;
        float: right;
        color:;
    }
    .chat-container {
        clear: both;
    }
</style>   
""",unsafe_allow_html=True)

for message in st.session_state.messages:
    role_class = "assistant-bubble" if message['role']=="assistant" else "user-bubble"
    
    st.markdown(f"""
        <div class="chat-container">
            <div class="{role_class}">
                <strong>{message['role'].upper()}:<//strong><br>
                {message['content']}
            </div>
        </div>
              
        """,unsafe_allow_html=True)

if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt.capitalize()})
    
    # ✅ Display user message with custom styling
    st.markdown(f"""
    <div class="chat-container">
        <div class="user-bubble">
            <div class="role-label"><strong>USER:</strong></div>
            {prompt.capitalize()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ✅ Display assistant response area with CUSTOM STYLING
    message_placeholder = st.empty()
    full_response = ""
    
    # Show "Thinking..." initially
    message_placeholder.markdown("""
    <div class="chat-container">
        <div class="assistant-bubble">
            <div class="role-label">ASSISTANT</div>
            <em>Thinking...</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
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
        
        # Stream the response with custom styling
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                # ✅ Update with custom styling and typing cursor
                message_placeholder.markdown(f"""
                <div class="chat-container">
                    <div class="assistant-bubble">
                        <div class="role-label"><strong>ASSISTANT:</strong></div>
                        {full_response}▌
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ✅ Final display without cursor
        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT</div>
                {full_response}
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.error(error_msg)
        # ✅ Error message with custom styling
        message_placeholder.markdown(f"""
        <div class="chat-container">
            <div class="assistant-bubble">
                <div class="role-label">ASSISTANT</div>
                Sorry, I encountered an error. Please try again.
            </div>
        </div>
        """, unsafe_allow_html=True)
        full_response = "Sorry, I encountered an error. Please try again."

    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

# ✅ Footer stays OUTSIDE the if block (always shows)
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Your personal AI assistant • Powered by Groq</p>
</div>
""", unsafe_allow_html=True)