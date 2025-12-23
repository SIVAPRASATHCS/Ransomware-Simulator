import streamlit as st
import time
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import random

# --- CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="Ransomware Simulator V2",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ADVANCED CSS & MOBILE OPTIMIZATION ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;600&display=swap');

    /* Variables */
    :root {
        --neon-green: #39ff14;
        --neon-red: #ff003c;
        --neon-blue: #00f3ff;
        --bg-dark: #050505;
        --card-bg: rgba(20, 20, 20, 0.9);
    }

    /* Global Reset */
    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(20, 20, 20, 0.8) 0%, rgba(0, 0, 0, 1) 100%),
            linear-gradient(rgba(0, 255, 0, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 0, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 20px 20px, 20px 20px;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Typography */
    h1, h2, h3, .glitch {
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }
    
    h1 { 
        color: var(--neon-blue); 
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 1px solid var(--neon-blue);
        color: var(--neon-blue);
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%; /* Mobile Friendly */
        padding: 0.8rem;
    }
    
    .stButton > button:hover {
        background: rgba(0, 243, 255, 0.1);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
        border-color: #fff;
        color: #fff;
    }

    /* Cards (Glassmorphism) */
    .cyber-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 3px solid var(--neon-blue);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Mobile Media Queries */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        .stButton > button { padding: 1rem; font-size: 1rem; }
        .cyber-card { padding: 1rem; }
    }
    
     /* Ransom Note Specifics */
    .ransom-container {
        border: 2px solid var(--neon-red);
        background: rgba(50, 0, 0, 0.9);
        color: var(--neon-red);
        animation: pulse 2s infinite;
        padding: 2rem;
        text-align: center;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0); }
    }

</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = 'education'
if 'target_folder' not in st.session_state: st.session_state.target_folder = None
if 'is_encrypted' not in st.session_state: st.session_state.is_encrypted = False
if 'key' not in st.session_state: st.session_state.key = b'01234567890123456789012345678901' 
if 'attack_start_time' not in st.session_state: st.session_state.attack_start_time = None
if 'quiz_score' not in st.session_state: st.session_state.quiz_score = 0
if 'attack_variant' not in st.session_state: st.session_state.attack_variant = 'Standard'

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### 🧭 NAVIGATION")
    if st.button("🏠 GO TO HOME SCREEN"):
        st.session_state.page = 'education'
        st.session_state.is_encrypted = False
        st.session_state.target_folder = None
        st.rerun()
    st.markdown("---")
    st.caption("Ransomware Simulator V2")

# --- LOGIC ---

def get_files_in_folder(folder_path):
    # Return list of uploaded files from session state
    if folder_path == "cloud_simulation" and 'uploaded_files' in st.session_state:
        return st.session_state.uploaded_files
    return []

def encrypt_file(file_obj):
    try:
        # Work with file-like objects (uploaded files)
        if hasattr(file_obj, 'read'):
            data = file_obj.read() if isinstance(file_obj.read(), bytes) else file_obj.getvalue()
        else:
            data = file_obj
        
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = iv + encryptor.update(data) + encryptor.finalize()
        
        # Store encrypted data in session state
        if 'encrypted_files' not in st.session_state:
            st.session_state.encrypted_files = {}
        
        filename = file_obj.name if hasattr(file_obj, 'name') else 'file'
        st.session_state.encrypted_files[filename + ".locked"] = encrypted_data
        return True
    except Exception as e:
        st.error(f"Encryption error: {e}")
        return False

def decrypt_file(filename):
    try:
        if 'encrypted_files' not in st.session_state:
            return False
        
        if filename not in st.session_state.encrypted_files:
            return False
            
        data = st.session_state.encrypted_files[filename]
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Store decrypted data
        if 'decrypted_files' not in st.session_state:
            st.session_state.decrypted_files = {}
        st.session_state.decrypted_files[filename[:-7]] = decrypted_data
        
        return True
    except Exception as e:
        st.error(f"Decryption error: {e}")
        return False

def select_folder():
    # Cloud-compatible: Use file uploads instead of folder selection
    st.markdown("**Upload files to simulate encryption:**")
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['txt', 'jpg', 'png', 'pdf', 'docx', 'xlsx'],
        help="Upload test files for the simulation (they will be encrypted in-memory only)"
    )
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        return "cloud_simulation"
    return None

def restore_files():
    if st.session_state.is_encrypted and 'encrypted_files' in st.session_state:
        for filename in list(st.session_state.encrypted_files.keys()):
            decrypt_file(filename)
        st.session_state.is_encrypted = False
        st.success("✅ Files decrypted! You can download them below.")

# --- PAGES ---

def page_education():
    st.markdown("<h1 style='text-align:center;'>RANSOMWARE SIMULATOR <span style='color:var(--neon-green); font-size:0.5em;'>V2.0</span></h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='cyber-card'>
        <h3>⚠️ SYSTEM WARNING</h3>
        <p>This is a safe, educational simulation environment designed to demonstrate the mechanics of ransomware attacks.</p>
        <hr style='border-color: rgba(255,255,255,0.1);'>
        <p style='color: var(--neon-green)'><b>MOBILE OPTIMIZED | REAL-TIME ENCRYPTION | INTERACTIVE LAB</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='cyber-card'><h3>🔍 The Threat</h3><p>Ransomware encrypts your data and demands payment. It often arrives via email attachments or cracked software.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='cyber-card'><h3>🛡️ The Defense</h3><p><b>Backups</b> are the only 100% guarantee. Antivirus helps, but human awareness is key.</p></div>", unsafe_allow_html=True)

    if st.button("INITIALIZE LAB ENVIRONMENT 🚀", use_container_width=True):
        st.session_state.page = "lab_setup"
        st.rerun()

def page_lab_setup():
    st.title("🧪 LAB CONFIGURATION")
    
    # Attack Variant Selector
    st.markdown("### 1. SELECT ATTACK PROFILE")
    variant = st.selectbox("Choose Malware Behavior:", ["Standard (CryptoLocker)", "Fast (WannaCry)", "Stealth (Background)"])
    st.session_state.attack_variant = variant
    
    st.markdown("### 2. SELECT BAIT FILE")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 Spotify_Premium_Mod.apk"):
            st.session_state.target_app_name = "Spotify Mod"
            st.session_state.show_warning = True
    with col2:
        if st.button("🎮 GTAV_Crack_Full.exe"):
            st.session_state.target_app_name = "GTA V Crack"
            st.session_state.show_warning = True
            
    if st.session_state.get('show_warning'):
        st.markdown(f"<div class='cyber-card' style='border-color: var(--neon-red); color: var(--neon-red);'>⚠️ WARNING: Unverified Source Detected: {st.session_state.target_app_name}</div>", unsafe_allow_html=True)
        
        if st.checkbox("IGNORE WARNING & PROCEED"):
            st.markdown("### 3. UPLOAD TARGET FILES")
            folder = select_folder()
            if folder:
                st.session_state.target_folder = folder
                st.success(f"📁 {len(st.session_state.uploaded_files)} files uploaded")
                
                if st.button("☠️ EXECUTE PAYLOAD"):
                    st.session_state.page = "attack_run"
                    st.rerun()

def page_attack_run():
    st.empty()
    st.markdown("<h1 style='color:var(--neon-green); text-align:center;'>INSTALLING...</h1>", unsafe_allow_html=True)
    
    bar = st.progress(0)
    term = st.empty()
    
    speed = 0.01 if "Fast" in st.session_state.attack_variant else 0.03
    
    for i in range(100):
        time.sleep(speed)
        bar.progress(i + 1)
        if i % 10 == 0: term.code(f"> unpacking_payload_chunk_{i}.bin ... OK")
    
    st.markdown("<h1 style='color:var(--neon-red); text-align:center; animation: glitch 0.3s infinite;'>⚠️ SYSTEM BREACHED ⚠️</h1>", unsafe_allow_html=True)
    time.sleep(1)
    
    # Encryption
    folder = st.session_state.target_folder
    files = get_files_in_folder(folder)
    
    if not st.session_state.is_encrypted:
        for f in files:
            encrypt_file(f)
            # Only show log if not fast mode to save rendering time
            if "Fast" not in st.session_state.attack_variant:
                filename = f.name if hasattr(f, 'name') else str(f)
                term.code(f"ENCRYPTING: {filename}")
                time.sleep(0.1)
        st.session_state.is_encrypted = True
        st.session_state.attack_start_time = datetime.now()
    
    st.session_state.page = "ransom_screen"
    st.rerun()

def page_ransom_screen():
    # Timer
    remaining = timedelta(minutes=2) # Default visual
    if st.session_state.attack_start_time:
        elapsed = datetime.now() - st.session_state.attack_start_time
        remaining = timedelta(minutes=2) - elapsed
        if remaining.total_seconds() <= 0:
            restore_files()
            st.session_state.page = "quiz"
            st.rerun()
            
    st.markdown(f"""
    <div class='ransom-container'>
        <h1 style='color:white; font-size: 3rem;'>FILES ENCRYPTED</h1>
        <p>IDENTIFIER: {st.session_state.attack_variant.upper()}</p>
        <h2 style='font-family: monospace;'>{str(remaining).split('.')[0]}</h2>
        <p>Send 0.5 BTC to unlock your data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
         if st.button("💸 PAY RANSOM (Simulate)"):
             st.error("❌ ERROR: PAYMENT SERVER OFFLINE. (Most gangs just steal your money!)")
    with col2:
        if st.button("🔓 DECRYPT (Education Mode)"):
            restore_files()
            st.session_state.page = "quiz"
            st.rerun()
    
    # Show encrypted files
    if 'encrypted_files' in st.session_state and st.session_state.encrypted_files:
        st.markdown("### 🔒 Encrypted Files:")
        for filename in st.session_state.encrypted_files.keys():
            st.text(f"❌ {filename}")
            
    time.sleep(1)
    st.rerun()

def page_quiz():
    # removed st.balloons() here
    st.title("✅ SYSTEM RESTORED")
    st.markdown("Files recovered. Now, let's verify your knowledge.")
    
    st.markdown("<div class='cyber-card'><h3>🧠 ADVANCED KNOWLEDGE CHECK</h3>", unsafe_allow_html=True)
    
    questions = {
        "q1": {"text": "1. What is the #1 most effective defense against ransomware?", 
               "options": ["Antivirus Software", "Regular Offline Backups", "Firewalls", "Strong Passwords"], 
               "answer": "Regular Offline Backups"},
        "q2": {"text": "2. Why are 'cracked' software downloads dangerous?", 
               "options": ["They are illegal", "They are often trojans for malware", "They use too much CPU", "They don't get updates"], 
               "answer": "They are often trojans for malware"},
        "q3": {"text": "3. What should be your FIRST action if you suspect infection?", 
               "options": ["Pay the ransom", "Disconnect from the Internet/Network", "Delete all files", "Restart the computer"], 
               "answer": "Disconnect from the Internet/Network"},
        "q4": {"text": "4. What does 'Phishing' refer to?", 
               "options": ["Fishing for compliments", "Fraudulent emails mimicking trusted sources", "Hacking WiFi", "A type of virus"], 
               "answer": "Fraudulent emails mimicking trusted sources"},
        "q5": {"text": "5. Does paying the ransom GUARANTEE you get your files back?", 
               "options": ["Yes, hackers are honest", "No, there is no guarantee", "Yes, legally they must", "Only if you pay in Bitcoin"], 
               "answer": "No, there is no guarantee"},
        "q6": {"text": "6. What is the purpose of Encryption in a ransomware attack?", 
               "options": ["To steal passwords", "To mine crypto", "To make data unreadable without a key", "To delete the OS"], 
               "answer": "To make data unreadable without a key"},
        "q7": {"text": "7. Which file extension should you be most wary of receiving in email?", 
               "options": [".pdf", ".jpg", ".exe / .vbs", ".txt"], 
               "answer": ".exe / .vbs"},
        "q8": {"text": "8. What is Multi-Factor Authentication (MFA)?", 
               "options": ["Using two passwords", "Using a password + a code from your phone", "Scanning for viruses", "Changing IP address"], 
               "answer": "Using a password + a code from your phone"},
        "q9": {"text": "9. If a pop-up says 'Your Computer is Infected, Call Support', it is likely:", 
               "options": ["A helpful Microsoft alert", "A Tech Support Scam", "A Windows update", "Real antivirus"], 
               "answer": "A Tech Support Scam"},
        "q10": {"text": "10. Why do attackers prefer cryptocurrency?", 
               "options": ["It is harder to trace than bank transfers", "It is worthless", "It is easy to buy", "Banks like it"], 
               "answer": "It is harder to trace than bank transfers"}
    }
    
    score = 0
    # Use a form so the page doesn't reload on every radio click
    with st.form("quiz_form"):
        user_answers = {}
        for k, v in questions.items():
            st.markdown(f"**{v['text']}**")
            # index=None ensures no default selection
            user_answers[k] = st.radio(label="Select Answer:", options=v["options"], key=k, index=None, label_visibility="collapsed")
            st.markdown("---")
            
        submitted = st.form_submit_button("SUBMIT ANSWERS")
        
    if submitted:
        for k, v in questions.items():
            if user_answers[k] == v["answer"]:
                score += 1
        
        st.session_state.quiz_score = score
        
        if score >= 9:
            st.success(f"🏆 ELITE DEFENDER! Score: {score}/10")
        elif score >= 7:
            st.info(f"✅ PASSED. Score: {score}/10. Good job.")
        else:
            st.error(f"❌ FAILED. Score: {score}/10. You need to review cyber hygiene basics.")
            
        st.markdown("### 🔍 Attack Timeline Summary")
        st.code(f"1. User downloaded {st.session_state.get('target_app_name')} (Trojan)\n2. Malware executed {st.session_state.attack_variant} encryption\n3. Files locked with AES-256\n4. User recovered via Simulation Tool")
        
        # Show download buttons for decrypted files
        if 'decrypted_files' in st.session_state and st.session_state.decrypted_files:
            st.markdown("### 📥 Download Decrypted Files:")
            for filename, data in st.session_state.decrypted_files.items():
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=data,
                    file_name=filename,
                    mime="application/octet-stream"
                )
        
        if st.button("RESTART SIMULATION"):
            # Clear all session state
            for key in ['page', 'is_encrypted', 'attack_start_time', 'uploaded_files', 
                       'encrypted_files', 'decrypted_files', 'target_folder']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = 'education'
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTER ---
pages = {
    'education': page_education,
    'lab_setup': page_lab_setup,
    'attack_run': page_attack_run,
    'ransom_screen': page_ransom_screen,
    'quiz': page_quiz
}

if st.session_state.page in pages:
    pages[st.session_state.page]()
