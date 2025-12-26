import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(
    page_title="Mock Interview Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            background: radial-gradient(circle at top right, #1e1e2e, #11111b);
            font-family: 'Inter', sans-serif;
            color: #cdd6f4;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] { 
            background-color: #181825 !important;
            border-right: 1px solid #313244 !important;
            min-width: 300px !important; 
            max-width: 300px !important; 
        }
        
        /* Sidebar Buttons */
        [data-testid="stSidebar"] .stButton button { 
            width: 100%; 
            border-radius: 8px; 
            font-weight: 600;
            background: #1e1e2e;
            border: 1px solid #313244;
            color: #bac2de;
            padding: 12px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background: #313244;
            border-color: #89b4fa;
            color: #f5e0dc;
        }
        
        /* Chat Messages */
        .stChatMessage {
            background-color: transparent !important;
            padding: 1.5rem 0 !important;
        }
        [data-testid="stChatMessageContent"] {
            background-color: #1e1e2e !important;
            border: 1px solid #313244 !important;
            border-radius: 16px !important;
            padding: 1rem 1.5rem !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        }
        
        /* Link Buttons */
        .stLinkButton > a {
            background: linear-gradient(90deg, #89b4fa, #b4befe) !important;
            color: #11111b !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            text-decoration: none !important;
        }
        
        /* Hide Streamlit Branding */
        header, footer, #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Strict Technical Interviewer System Instruction
INTERVIEW_INSTRUCTION = """
You are a Strict Technical Interviewer conducting a professional technical interview.

RULES:
1. Ask ONLY ONE question at a time.
2. After the candidate answers, provide:
   - **Score:** X/10
   - **Feedback:** Brief analysis of their answer (2-3 sentences)
   - **Next Question:** Immediately ask the next relevant question

3. Questions should be appropriate for the candidate's target role and company.
4. Progress from easier to harder questions naturally.
5. Be professional, direct, and constructive in feedback.
6. Do not repeat questions.
7. Challenge the candidate but remain fair.
"""

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=INTERVIEW_INSTRUCTION
)

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.header("🎯 Mock Interview Engine")
    
    # MANUAL INPUTS
    target_role = st.text_input("💼 Target Role:", "Software Engineer")
    target_company = st.text_input("🏭 Target Company:", "Amazon")
    
    st.markdown("---")
    
    # START INTERVIEW BUTTON
    if st.button("🚀 Start Mock Interview", type="primary", use_container_width=True):
        # Clear messages and start fresh
        st.session_state.messages = []
        st.session_state.interview_started = True
        
        # Generate first question immediately
        first_prompt = f"I am interviewing for a {target_role} position at {target_company}. Start the interview by asking me the first technical question. Do not introduce yourself, just ask the question directly."
        
        try:
            response = model.generate_content(first_prompt)
            if response.candidates and response.candidates[0].content.parts:
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error starting interview: {str(e)}"})
        
        st.rerun()
    
    st.markdown("---")
    
    # SESSION HISTORY
    st.subheader("📜 Session History")
    if not st.session_state.messages:
        st.write("_No conversation yet. Start an interview!_")
    else:
        st.write(f"📊 Total exchanges: {len([m for m in st.session_state.messages if m['role'] == 'user'])}")
        st.markdown("---")
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                snippet = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                st.text(f"❓ Q{i//2 + 1}: {snippet}")
            elif msg["role"] == "assistant":
                snippet = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                st.text(f"💬 A: {snippet}")
    
    st.markdown("---")
    st.success("✅ System Ready")

# --- 5. MAIN CHAT INTERFACE ---
st.title("🎯 Mock Interview Session")
if st.session_state.interview_started:
    st.markdown(f"**Interviewing for:** {target_role} at {target_company}")
else:
    st.markdown("_Configure your role and company in the sidebar, then click 'Start Mock Interview'_")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Logic
if prompt := st.chat_input("Type your answer here..."):
    # 1. Append & Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Generate AI Response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Evaluating your answer..."):
                # Build context for the interview
                interview_context = f"Context: Interviewing for {target_role} at {target_company}. Candidate's answer: {prompt}\n\nProvide score, feedback, and next question as instructed."
                response = model.generate_content(interview_context)
                
                # --- SAFETY CHECK: Verify AI returned valid content ---
                if response.candidates and response.candidates[0].content.parts:
                    ai_text = response.text
                    st.markdown(ai_text)
                    
                    # Add YouTube search button for interview prep
                    search_query = f"{target_role}+{target_company}+interview+preparation".replace(" ", "+")
                    st.markdown("---")
                    st.link_button("▶️ Search Interview Prep Tutorials", f"https://www.youtube.com/results?search_query={search_query}")
                    
                    # Save AI response to memory
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                else:
                    # AI returned empty response - show finish reason for debugging
                    finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"
                    error_msg = f"⚠️ The AI could not generate a response. (Reason: {finish_reason})"
                    st.warning(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                # --------------------------------------------
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
