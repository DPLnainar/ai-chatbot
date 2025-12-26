import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import re
from collections import Counter

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(
    page_title="Elite Career Companion",
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

# --- 3. COMPANY-SPECIFIC INSTRUCTIONS ---
COMPANY_INSTRUCTIONS = {
    "General Interview Practice": """You are a Professional Technical Interview Coach helping students prepare for placements.
    - Ask balanced technical questions covering fundamentals and problem-solving
    - Provide constructive feedback after each answer
    - Offer suggestions for improvement
    - Be encouraging yet honest about areas needing work""",
    
    "TCS Ninja (3.36 LPA)": """You are a TCS Ninja Interviewer (Service-based company, entry-level role).
    - Focus on basic programming fundamentals (C, Java, Python basics)
    - Ask questions about data structures, simple algorithms
    - Test basic aptitude and logical reasoning
    - Keep difficulty moderate - TCS looks for consistent performers with good fundamentals""",
    
    "Amazon SDE": """You are an Amazon SDE Interviewer conducting a rigorous technical round.
    - Focus heavily on Data Structures & Algorithms (arrays, trees, graphs, dynamic programming)
    - Ask about system design for scalability
    - Emphasize Amazon Leadership Principles in behavioral questions
    - Expect optimal solutions with time/space complexity analysis""",
    
    "Google SWE": """You are a Google Software Engineer Interviewer.
    - Ask challenging algorithmic problems requiring creative thinking
    - Focus on clean code, edge cases, and optimization
    - Test for Googleyness (collaboration, innovation, impact)
    - Expect candidates to explain their thought process clearly""",
    
    "Wipro Elite/WILP": """You are a Wipro Elite Program Interviewer.
    - Test fundamentals in programming, DBMS, OS, Networks
    - Ask about project experience and practical applications
    - Focus on learning agility and adaptability
    - Keep questions balanced between theory and practical scenarios""",
    
    "HR Round (Any Company)": """You are an HR Interviewer conducting a final screening round.
    - Ask about strengths, weaknesses, career goals
    - Inquire about teamwork, conflict resolution, and leadership experiences
    - Assess cultural fit and communication skills
    - Be friendly yet professional, testing emotional intelligence"""
}

# --- 4. HELPER FUNCTIONS ---
def analyze_resume(pdf_file):
    """Extract text from PDF and perform ATS scoring"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Keyword categories for ATS scoring
        keywords = {
            "Programming": ["python", "java", "c++", "javascript", "sql", "html", "css", "react", "node"],
            "Web Tech": ["django", "flask", "fastapi", "rest api", "mongodb", "postgresql", "mysql"],
            "Database": ["sql", "nosql", "mongodb", "postgresql", "mysql", "database"],
            "Cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "ci/cd"],
            "Tools": ["git", "github", "linux", "agile", "jira"],
            "Concepts": ["oop", "data structures", "algorithms", "system design", "machine learning"]
        }
        
        text_lower = text.lower()
        found_keywords = {}
        missing_keywords = {}
        
        for category, words in keywords.items():
            found = [w for w in words if w in text_lower]
            missing = [w for w in words if w not in text_lower]
            found_keywords[category] = found
            missing_keywords[category] = missing
        
        # Calculate ATS score (0-100)
        total_keywords = sum(len(words) for words in keywords.values())
        total_found = sum(len(found) for found in found_keywords.values())
        keyword_score = (total_found / total_keywords) * 60  # 60% weight
        
        # Check for action verbs
        action_verbs = ["developed", "implemented", "designed", "optimized", "built", "created", "led", "managed"]
        action_verb_count = sum(1 for verb in action_verbs if verb in text_lower)
        action_verb_score = min(action_verb_count * 2.5, 20)  # 20% weight, max 20
        
        # Basic format check
        format_score = 20 if len(text) > 500 else 10  # 20% weight
        
        ats_score = int(keyword_score + action_verb_score + format_score)
        
        return {
            "text": text,
            "ats_score": ats_score,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "action_verb_count": action_verb_count,
            "recommendations": f"Add more keywords from missing categories and use action verbs."
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_speech_fillers(text):
    """Detect filler words in candidate's response"""
    fillers = ["um", "uh", "like", "basically", "actually", "you know", "i mean", "sort of", "kind of"]
    text_lower = text.lower()
    
    filler_counts = {f: len(re.findall(r'\b' + f + r'\b', text_lower)) for f in fillers}
    total_fillers = sum(filler_counts.values())
    word_count = len(text.split())
    
    confidence_rating = max(1, 10 - (total_fillers * 2))  # Deduct 2 points per filler
    
    return {
        "total_fillers": total_fillers,
        "filler_breakdown": filler_counts,
        "word_count": word_count,
        "confidence_rating": confidence_rating,
        "feedback": "Great clarity!" if total_fillers == 0 else f"Try to reduce filler words like '{', '.join([f for f, c in filler_counts.items() if c > 0])}'"
    }

# --- 5. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_company" not in st.session_state:
    st.session_state.selected_company = "General Interview Practice"

if "target_role" not in st.session_state:
    st.session_state.target_role = "Software Engineer"

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("📋 Resume Analyzer")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            result = analyze_resume(uploaded_file)
            if "error" not in result:
                st.metric("ATS Score", f"{result['ats_score']}/100")
                
                with st.expander("📊 Detailed Report"):
                    st.write("**Found Keywords:**")
                    for cat, words in result['found_keywords'].items():
                        if words:
                            st.write(f"- {cat}: {', '.join(words)}")
                    
                    st.write("\n**Missing Keywords (Add these!):**")
                    for cat, words in result['missing_keywords'].items():
                        if words:
                            st.write(f"- {cat}: {', '.join(words[:3])}")
                    
                    st.write(f"\n**Action Verbs:** {result['action_verb_count']}")
                    st.info(result['recommendations'])
            else:
                st.error(f"Error: {result['error']}")
    
    st.markdown("---")
    st.header("🎯 Company Drill Mode")
    
    st.session_state.selected_company = st.selectbox(
        "Select Interview Type:",
        list(COMPANY_INSTRUCTIONS.keys())
    )
    
    st.session_state.target_role = st.text_input("💼 Target Role:", st.session_state.target_role)
    
    st.markdown("---")
    st.caption("💡 **Tip:** Upload your resume first to get personalized feedback!")

# --- 7. MAIN CONTENT ---
# Dynamic title based on selected company
company_display = st.session_state.selected_company.replace(" Interview Practice", "").replace(" (3.36 LPA)", "")
st.title(f"Hello, Future Engineer 🚀")
st.subheader(f"**{company_display}** Interview Preparation")

# Initialize AI model with selected company instructions
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=COMPANY_INSTRUCTIONS[st.session_state.selected_company]
)

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT INPUT ---
if prompt := st.chat_input(f"Ask anything about {st.session_state.selected_company} interviews..."):
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Generate AI Response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                
                # Safety check
                if response.candidates and response.candidates[0].content.parts:
                    ai_text = response.text
                    st.markdown(ai_text)
                    
                    # For interview companies, show speech analysis
                    if st.session_state.selected_company != "General Interview Practice":
                        speech_analysis = analyze_speech_fillers(prompt)
                        st.markdown("---")
                        st.caption(f"**Communication Score:** {speech_analysis['confidence_rating']}/10 | {speech_analysis['feedback']}")
                    
                    # YouTube resource button
                    search_query = f"{st.session_state.selected_company}+{st.session_state.target_role}+interview+preparation".replace(" ", "+")
                    st.link_button("▶️ YouTube Interview Resources", f"https://www.youtube.com/results?search_query={search_query}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                else:
                    finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"
                    error_msg = f"⚠️ Could not generate response. (Reason: {finish_reason})"
                    st.warning(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
