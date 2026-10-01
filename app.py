import streamlit as st
import imaplib
import email
from openai import OpenAI

# 1. Configurazione della pagina Streamlit
st.set_page_config(
    page_title="AI Secretary",
    page_icon="🤖",
    layout="centered"
)

# 2. UI/UX Minimal e Moderna (Contrasti elevati e pulizia visiva)
st.markdown("""
    <style>
    .stApp {
        background: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }
    
    /* Card minimali ed eleganti */
    .clean-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    /* Pulsanti */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
    }
    
    h1, h2, h3 {
        color: #0f172a;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione dello stato di sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ==========================================
# SEZIONE 1: LOGIN (PASSKEY / MANUALE)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
    st.title("🤖 AI Secretary")
    st.markdown("### Accesso")
    
    tab_face, tab_manual = st.tabs(["👤 Riconoscimento Facciale", "🔑 Manuale"])
    
    with tab_face:
        if st.button("✨ Entra con Passkey", type="primary"):
            st.session_state.logged_in = True
            st.session_state.email_user = "nicolafronte@icloud.com"
            st.session_state.email_password = "dwhh-jmgx-shmj-ulwa"
            st.session_state.openai_key = "Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA"
            st.rerun()

    with tab_manual:
        manual_email = st.text_input("Email", value="nicolafronte@icloud.com")
        manual_pass = st.text_input("Password App", type="password", value="dwhh-jmgx-shmj-ulwa")
        manual_key = st.text_input("OpenAI Key", type="password", value="Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA")
        
        if st.button("Accedi", type="primary"):
            if manual_email and manual_pass and manual_key:
                st.session_state.logged_in = True
                st.session_state.email_user = manual_email
                st.session_state.email_password = manual_pass
                st.session_state.openai_key = manual_key
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# SEZIONE 2: DASHBOARD PRINCIPALE
# ==========================================
else:
    with st.sidebar:
        if st.button("Disconnetti"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
    st.title("📬 Posta in Arrivo")

    if st.button("🚀 Avvia controllo email", type="primary"):
        with st.spinner("Analisi in corso..."):
            try:
                mail = imaplib.IMAP4_SSL("imap.mail.me.com")
                mail.login(st.session_state.email_user, st.session_state.email_password)
                mail.select("inbox")

                status, messages = mail.search(None, 'UNSEEN')
                
                if status == 'OK':
                    raw_messages = messages[0]
                    if raw_messages:
                        email_ids = raw_messages.split()
                        if email_ids:
                            client = OpenAI(api_key=st.session_state.openai_key)
                            
                            for e_id in email_ids[-3:]:
                                res, msg_data = mail.fetch(e_id, '(RFC822)')
                                for response_part in msg_data:
                                    if isinstance(response_part, tuple):
                                        msg = email.message_from_bytes(response_part[1])
                                        subject = msg["Subject"] or "Senza oggetto"
                                        sender = msg["From"] or "Sconosciuto"
                                        
                                        body = ""
                                        if msg.is_multipart():
                                            for part in msg.walk():
                                                if part.get_content_type() == "text/plain":
                                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                                    break
                                        else:
                                            body = msg.get_payload(decode=True).decode(errors='ignore')

                                        prompt = f"Mittente: {sender}\nOggetto: {subject}\nTesto:\n{body[:1000]}"
                                        
                                        response = client.chat.completions.create(
                                            model="gpt-4o-mini",
                                            messages=[
                                                {"role": "system", "content": "Sei un segretario efficiente. Riassumi questa email in modo chiaro e indica se richiede un'azione urgente."},
                                                {"role": "user", "content": prompt}
                                            ]
                                        )
                                        
                                        analysis = response.choices[0].message.content
                                        
                                        with st.expander(f"📩 {subject}"):
                                            st.write(analysis)
                                            
                mail.logout()
                
            except Exception as e:
                st.error("Errore di connessione o elaborazione.")
    st.markdown("</div>", unsafe_allow_html=True)
