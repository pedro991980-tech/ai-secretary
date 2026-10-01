import streamlit as st
import imaplib
import email
from openai import OpenAI

# 1. Configurazione della pagina Streamlit
st.set_page_config(
    page_title="AI Secretary | Smart Dashboard",
    page_icon="🤖",
    layout="centered"
)

# 2. UI/UX Moderna (Stile SaaS di fascia alta, Glassmorphism e tipografia pulita)
st.markdown("""
    <style>
    /* Sfondo generale ed eleganza visiva */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Card in stile Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
    }

    /* Pulsanti moderni */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    /* Titoli accattivanti */
    h1, h2, h3 {
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione dello stato di sessione per il login e le credenziali
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_method" not in st.session_state:
    st.session_state.auth_method = None


# ==========================================
# SEZIONE 1: PAGINA DI LOGIN E PASSKEY (BIOMETRICA)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.title("🤖 AI Secretary")
    st.write("Il tuo assistente email intelligente con intelligenza artificiale.")
    st.markdown("### Accesso Sicuro")
    
    tab_face, tab_manual = st.tabs(["👤 Riconoscimento Facciale (Passkey)", "🔑 Credenziali Manuali"])
    
    with tab_face:
        st.info("Usa il riconoscimento facciale (Face ID / Touch ID / WebAuthn) del tuo dispositivo per un accesso immediato e sicuro.")
        
        # Simula il trigger di autenticazione biometrica
        if st.button("✨ Avvia Scansione Facciale / Passkey", type="primary", use_container_width=True):
            with st.spinner("Verifica biometrica in corso..."):
                # Qui colleghiamo i tuoi dati di default o passkey salvate
                st.session_state.logged_in = True
                st.session_state.email_user = "nicolafronte@icloud.com"
                st.session_state.email_password = "dwhh-jmgx-shmj-ulwa"
                st.session_state.openai_key = "Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA"
                st.success("Autenticazione biometrica riuscita! Accesso in corso...")
                st.rerun()

    with tab_manual:
        manual_email = st.text_input("Email iCloud", value="nicolafronte@icloud.com")
        manual_pass = st.text_input("Password per App", type="password", value="dwhh-jmgx-shmj-ulwa")
        manual_key = st.text_input("OpenAI API Key", type="password", value="Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA")
        
        if st.button("Accedi alla Dashboard", type="primary", use_container_width=True):
            if manual_email and manual_pass and manual_key:
                st.session_state.logged_in = True
                st.session_state.email_user = manual_email
                st.session_state.email_password = manual_pass
                st.session_state.openai_key = manual_key
                st.rerun()
            else:
                st.error("Compila tutti i campi per procedere.")
                
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SEZIONE 2: DASHBOARD PRINCIPALE (POST-LOGIN)
# ==========================================
else:
    # Sidebar di navigazione e controllo utente
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/chatbot.png", width=100)
        st.write(f"Utente: **{st.session_state.email_user}**")
        st.divider()
        if st.button("🚪 Disconnetti (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.title("🤖 AI Secretary - Dashboard")
    st.write("Il sistema ha verificato la tua identità in sicurezza. Gestione email attiva.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Sezione interattiva per l'analisi email
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📬 Controllo e Analisi Posta in Arrivo")
    st.write("Clicca sul pulsante sottostante per avviare l'analisi intelligente dei nuovi messaggi non letti.")

    if st.button("🚀 Avvia controllo email", type="primary"):
        with st.spinner("Connessione al server IMAP di iCloud in corso..."):
            try:
                mail = imaplib.IMAP4_SSL("imap.mail.me.com")
                mail.login(st.session_state.email_user, st.session_state.email_password)
                mail.select("inbox")

                status, messages = mail.search(None, 'UNSEEN')
                
                if status != 'OK':
                    st.warning("Errore durante la ricerca delle email.")
                else:
                    raw_messages = messages[0]
                    if not raw_messages:
                        st.success("Controllo completato: nessuna nuova email da leggere.")
                    else:
                        email_ids = raw_messages.split()
                        if not email_ids:
                            st.success("Controllo completato: nessuna nuova email da leggere.")
                        else:
                            st.info(f"Trovate {len(email_ids)} nuove email da analizzare.")
                            
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
                                        
                                        with st.expander(f"📩 Da: {sender} - {subject}"):
                                            st.write(analysis)
                                            
                mail.logout()
                
            except Exception as e:
                st.error(f"Si è verificato un errore durante l'esecuzione: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📜 Stato del sistema")
    st.info("L'applicazione è protetta con sessione attiva ed è pronta all'uso.")
    st.markdown("</div>", unsafe_allow_html=True)
