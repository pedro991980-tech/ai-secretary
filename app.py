import streamlit as st
import imaplib
import email
from email.header import decode_header
from openai import OpenAI
import sqlite3
import hashlib
import os

# 1. Configurazione della pagina
st.set_page_config(
    page_title="AI Secretary Pro",
    page_icon="🤖",
    layout="centered"
)

# 2. UI/UX Moderna e di Classe (Stile SaaS Enterprise)
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
        font-size: 1.1rem;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        background-color: #2563eb;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    h1, h2, h3 {
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Inizializzazione Database SQLite per la persistenza degli utenti
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            app_password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Funzione di hashing per la sicurezza delle password salvate
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Funzione di decodifica header email
def decode_email_header(header_value):
    if not header_value:
        return "Sconosciuto"
    decoded_fragments = decode_header(header_value)
    result = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            if encoding:
                try:
                    result.append(fragment.decode(encoding, errors="ignore"))
                except:
                    result.append(fragment.decode("utf-8", errors="ignore"))
            else:
                result.append(fragment.decode("utf-8", errors="ignore"))
        else:
            result.append(str(fragment))
    return "".join(result)

# Gestione dello stato di sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# Recupero centralizzato della chiave OpenAI dai segreti di Streamlit (o fallback)
try:
    CENTRAL_OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
except:
    CENTRAL_OPENAI_KEY = "" # Inserisci qui una chiave di fallback se non usi i secrets


# ==========================================
# SEZIONE 1: AUTENTICAZIONE E REGISTRAZIONE (PERSISTENTE)
# ==========================================
if not st.session_state.logged_in:
    with st.sidebar:
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
        else:
            st.markdown("### 🤖 AI Secretary")
        st.markdown("---")
        st.info("Accedi con la tua email e la password specifica per app per mantenere attiva la sessione.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.title("🤖 AI Secretary")
        st.markdown("<p style='color: #64748b;'>Piattaforma intelligente di gestione email.</p>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 Accedi", "📝 Registrati"])
        
        with tab_login:
            login_email = st.text_input("Email", placeholder="nome@dominio.com", key="l_email")
            login_pass = st.text_input("Password per App", type="password", placeholder="••••••••••••", key="l_pass")
            
            if st.button("Login al Sistema", type="primary"):
                if login_email and login_pass:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT app_password FROM users WHERE email = ?", (login_email.strip(),))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row and row[0] == hash_password(login_pass.strip()):
                        st.session_state.logged_in = True
                        st.session_state.user_email = login_email.strip()
                        st.session_state.user_pass = login_pass.strip()
                        st.success("Accesso effettuato con successo!")
                        st.rerun()
                    else:
                        st.error("Credenziali non valide o utente non registrato.")
                else:
                    st.warning("Inserisci tutti i campi.")

        with tab_register:
            reg_email = st.text_input("Tua Email", placeholder="nome@dominio.com", key="r_email")
            reg_pass = st.text_input("Password per App", type="password", placeholder="••••••••••••", key="r_pass")
            
            if st.button("Registrati Ora", type="primary"):
                if reg_email and reg_pass:
                    try:
                        conn = sqlite3.connect("users.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (email, app_password) VALUES (?, ?)", 
                                       (reg_email.strip(), hash_password(reg_pass.strip())))
                        conn.commit()
                        conn.close()
                        st.success("Registrazione completata! Ora puoi effettuare il login.")
                    except sqlite3.IntegrityError:
                        st.error("Questo indirizzo email risulta già registrato.")
                else:
                    st.warning("Compila tutti i campi per registrarti.")
                    
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# SEZIONE 2: DASHBOARD PRINCIPALE (POST-LOGIN)
# ==========================================
else:
    with st.sidebar:
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
        st.write(f"👤 **Account:** {st.session_state.user_email}")
        st.divider()
        if st.button("Disconnetti (Logout)"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.title("📬 Posta in Arrivo")
    st.markdown("<p style='color: #64748b;'>Analisi automatica e intelligente dei messaggi non letti.</p>", unsafe_allow_html=True)

    if st.button("🚀 Avvia Scansione Intelligente", type="primary"):
        with st.spinner("Connessione protetta al server IMAP e analisi in corso..."):
            try:
                # Rilevamento automatico del server IMAP
                email_lower = st.session_state.user_email.lower()
                if "gmail.com" in email_lower:
                    imap_server = "imap.gmail.com"
                elif "icloud.com" in email_lower or "me.com" in email_lower:
                    imap_server = "imap.mail.me.com"
                elif "outlook.com" in email_lower or "hotmail.com" in email_lower or "live.com" in email_lower:
                    imap_server = "imap-mail.outlook.com"
                else:
                    imap_server = "imap.mail.me.com"

                # Recupero password dalla sessione o database (qui usiamo la password temporanea in sessione dopo il login)
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(st.session_state.user_email, st.session_state.user_pass)
                mail.select("inbox")

                status, messages = mail.search(None, 'UNSEEN')
                
                if status != 'OK':
                    st.error("Errore durante la ricerca delle email.")
                else:
                    raw_messages = messages[0]
                    if not raw_messages:
                        st.success("Casella di posta pulita: nessuna nuova email.")
                    else:
                        email_ids = raw_messages.split()
                        if not email_ids:
                            st.success("Casella di posta pulita: nessuna nuova email.")
                        else:
                            st.info(f"Trovate {len(email_ids)} nuove email da analizzare.")
                            
                            # Inizializzazione OpenAI con la chiave centralizzata
                            client = OpenAI(api_key=CENTRAL_OPENAI_KEY)
                            
                            for e_id in email_ids[-3:]:
                                res, msg_data = mail.fetch(e_id, '(RFC822)')
                                for response_part in msg_data:
                                    if isinstance(response_part, tuple):
                                        msg = email.message_from_bytes(response_part[1])
                                        subject = decode_email_header(msg["Subject"])
                                        sender = decode_email_header(msg["From"])
                                        
                                        body = ""
                                        if msg.is_multipart():
                                            for part in msg.walk():
                                                if part.get_content_type() == "text/plain":
                                                    payload = part.get_payload(decode=True)
                                                    if payload:
                                                        body = payload.decode(errors='ignore')
                                                        break
                                        else:
                                            payload = msg.get_payload(decode=True)
                                            if payload:
                                                body = payload.decode(errors='ignore')

                                        prompt = f"Mittente: {sender}\nOggetto: {subject}\nTesto:\n{body[:1000]}"
                                        
                                        response = client.chat.completions.create(
                                            model="gpt-4o-mini",
                                            messages=[
                                                {"role": "system", "content": "Sei un segretario esecutivo efficiente. Riassumi questa email in modo chiaro e indica se richiede un'azione urgente."},
                                                {"role": "user", "content": prompt}
                                            ]
                                        )
                                        
                                        analysis = response.choices[0].message.content
                                        
                                        with st.expander(f"📩 Da: {sender} — {subject}"):
                                            st.markdown(analysis)
                                            
                mail.logout()
                
            except Exception as e:
                st.error(f"Errore di autenticazione o connessione IMAP: {e}")
                
    st.markdown("</div>", unsafe_allow_html=True)
