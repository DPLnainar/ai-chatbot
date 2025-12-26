import streamlit as st
import sqlite3
import google.generativeai as genai
# If Pylance still complains, you can ignore it as the code works at runtime.
# The google-generativeai package uses dynamic exports.

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Elite Career Companion",
    layout="wide",
    initial_sidebar_state="expanded"
)

# *** IMPORTANT: PASTE YOUR API KEY HERE ***
GOOGLE_API_KEY = "AIzaSyBKuIyBS5gmS49wEMdJJgIYKRWabNBN_TQ"

# Configure Gemini
if GOOGLE_API_KEY and "YOUR_API_KEY" not in GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)  # type: ignore
else:
    st.warning("⚠️ Please replace 'YOUR_API_KEY_HERE' in the code with your actual Google API Key.")

# --- 2. CSS STYLING (Professional Modern UI) ---
def inject_custom_css():
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
        section[data-testid="stSidebar"] {
            background-color: #181825 !important;
            border-right: 1px solid #313244 !important;
            min-width: 300px !important;
            max-width: 300px !important;
        }
        
        /* Sidebar Buttons */
        [data-testid="stSidebar"] div.stButton > button {
            text-align: left;
            background: #1e1e2e;
            border: 1px solid #313244;
            color: #bac2de;
            width: 100%;
            border-radius: 8px;
            padding: 10px 15px;
            margin-bottom: 5px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background: #313244;
            border-color: #45475a;
            color: #f5e0dc;
            transform: translateX(5px);
        }
        
        /* Action Buttons (Rename/Delete) */
        [data-testid="stSidebar"] div.stButton > button[help="Rename"]:hover {
            color: #89b4fa !important;
            background: rgba(137, 180, 250, 0.1) !important;
        }
        [data-testid="stSidebar"] div.stButton > button[help="Delete"]:hover {
            color: #f38ba8 !important;
            background: rgba(243, 139, 168, 0.1) !important;
        }
        
        /* New Chat Button */
        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #89b4fa, #b4befe) !important;
            color: #11111b !important;
            font-weight: 600 !important;
            border: none !important;
        }

        /* Chat Input */
        .stChatInputContainer {
            padding-bottom: 2rem !important;
            background: transparent !important;
        }
        .stChatInputContainer > div {
            background-color: #1e1e2e !important;
            border: 1px solid #313244 !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
        }
        
        /* Professional Cards */
        .card-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            padding: 1rem 0;
        }
        
        div[data-testid="stVerticalBlock"] > div > div > div > div.stButton > button {
            background: rgba(30, 30, 46, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            color: #cdd6f4 !important;
            border: 1px solid #313244 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            height: auto !important;
            min-height: 140px !important;
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            justify-content: center !important;
            text-align: left !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }
        
        div[data-testid="stVerticalBlock"] > div > div > div > div.stButton > button:hover {
            background: rgba(49, 50, 68, 0.8) !important;
            border-color: #89b4fa !important;
            box-shadow: 0 8px 32px rgba(137, 180, 250, 0.2) !important;
            transform: translateY(-8px) !important;
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
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #11111b; }
        ::-webkit-scrollbar-thumb { background: #313244; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #45475a; }

        /* Hide Streamlit Branding */
        header, footer, #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- 3. DATABASE ---
def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def create_session(title):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO sessions (title) VALUES (?)", (title,))
    sess_id = c.lastrowid
    conn.commit()
    conn.close()
    return sess_id

def get_sessions():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT id, title FROM sessions ORDER BY created_at DESC")
    return c.fetchall()

def save_message(sess_id, role, content):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (sess_id, role, content))
    conn.commit()
    conn.close()

def load_messages(sess_id):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC", (sess_id,))
    return [{"role": r, "content": t} for r, t in c.fetchall()]

def delete_session(sess_id):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (sess_id,))
    c.execute("DELETE FROM sessions WHERE id = ?", (sess_id,))
    conn.commit()
    conn.close()

def rename_session(sess_id, new_title):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, sess_id))
    conn.commit()
    conn.close()

init_db()

# --- 4. API SETUP (The Resource Curator Mode) ---
try:
    if GOOGLE_API_KEY and "YOUR_API_KEY" not in GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # We add a "System Instruction" to force the bot to give resources
        model = genai.GenerativeModel(
            'gemini-flash-latest',
            system_instruction="""
                You are an Elite Tech Mentor. Your goal is to help students master skills fast.
                
                Strict Response Rules:
                1. Direct Answer: Explain the concept simply (2-3 sentences).
                2. The "Why": Explain why this is important in the industry.
                3. 📚 Top Resources (MANDATORY):
                   - Provide 2-3 specific YouTube Channel names or Video Titles to search for (e.g., "Traversy Media", "Fireship").
                   - Provide 1 official documentation link (e.g., MDN, React Docs).
                4. 🚀 Actionable Step: Give one small code task to practice immediately.
            """
        )
    else:
        model = None
except Exception as e:
    st.error(f"API Key Error: {e}")
    model = None

# --- 5. THE AI FUNCTION (GEMINI WITH RESOURCES) ---
def get_gemini_response(prompt):
    try:
        if not GOOGLE_API_KEY or "YOUR_API_KEY" in GOOGLE_API_KEY:
            return "⚠️ API Key missing. Please open app.py and add your Google API Key."
        
        if model is None:
            return "⚠️ Model not initialized. Check your API key configuration."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {str(e)}"

# --- 6. APP LOGIC ---
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.markdown("""
        <div style='padding: 1rem 0; text-align: center;'>
            <h2 style='color: #89b4fa; margin-bottom: 0;'>Elite AI</h2>
            <p style='color: #585b70; font-size: 0.8rem;'>v2.0.4 • System Ready</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Recent")
    for s_id, title in get_sessions():
        col_chat, col_ren, col_del = st.columns([0.7, 0.15, 0.15])
        with col_chat:
            if st.button(f"💬 {title}", key=f"s_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.session_state.messages = load_messages(s_id)
                st.rerun()
        with col_ren:
            if st.button("✏️", key=f"ren_{s_id}", help="Rename"):
                st.session_state[f"renaming_{s_id}"] = True
        with col_del:
            if st.button("🗑️", key=f"del_{s_id}", help="Delete"):
                delete_session(s_id)
                if st.session_state.current_session_id == s_id:
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                st.rerun()
        
        if st.session_state.get(f"renaming_{s_id}", False):
            with st.container():
                new_name = st.text_input("New name", value=title, key=f"input_{s_id}", label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save", key=f"save_{s_id}", use_container_width=True):
                        if new_name:
                            rename_session(s_id, new_name)
                        st.session_state[f"renaming_{s_id}"] = False
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"can_{s_id}", use_container_width=True):
                        st.session_state[f"renaming_{s_id}"] = False
                        st.rerun()

# MAIN AREA
if st.session_state.current_session_id is None:
    st.container(height=120, border=False)
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #89b4fa; font-size: 3.5rem; font-weight: 700; margin-bottom: 0.5rem;'>Elite Career Companion</h1>
            <p style='color: #bac2de; font-size: 1.4rem; font-weight: 300;'>Your AI-powered journey to professional excellence starts here.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Starters (2x2 Grid)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 **Resume Intelligence**\n\nOptimize your profile with AI-driven feedback and industry standards.", use_container_width=True):
            new_id = create_session("Resume Review")
            st.session_state.current_session_id = new_id
            st.rerun()
        
        if st.button("💻 **Technical Mastery**\n\nDeep dive into complex concepts with personalized learning paths.", use_container_width=True):
            new_id = create_session("Tech Skills")
            st.session_state.current_session_id = new_id
            st.rerun()
            
    with col2:
        if st.button("🎯 **Interview Simulation**\n\nPractice high-stakes interviews with real-time behavioral analysis.", use_container_width=True):
            new_id = create_session("Mock Interview")
            st.session_state.current_session_id = new_id
            st.rerun()
            
        if st.button("🚀 **Strategic Career Path**\n\nMap out your long-term goals with data-backed career roadmaps.", use_container_width=True):
            new_id = create_session("Career Path")
            st.session_state.current_session_id = new_id
            st.rerun()

else:
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input & Response
    if prompt := st.chat_input("Ask Gemini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_message(st.session_state.current_session_id, "user", prompt)
        
        # Simple Response
        with st.spinner("Thinking..."):
            ai_response = get_gemini_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        save_message(st.session_state.current_session_id, "assistant", ai_response)
