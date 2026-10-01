import streamlit as st
import imaplib
import email
from openai import OpenAI
import json

# 1. Configurazione della pagina Streamlit
st.set_page_config(
    page_title="AI Secretary Pro",
    page_icon="🤖",
    layout="wide"
)

# 2. UI/UX Moderna e Pulita (Stile Dashboard SaaS)
st.markdown("""
    <style>
    .stApp {
        background: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }
    .clean-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
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
if "email_user" not in st.session_state:
    st.session_state.email_user = ""
if "email_password" not in st.session_state:
    st.session_state.email_password = ""
if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""


# ==========================================
# SEZIONE 1: LOGIN
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
        st.title("🤖 AI Secretary")
        st.markdown("<p style='color: #64748b;'>Il tuo assistente email intelligente e sicuro.</p>", unsafe_allow_html=True)
        
        tab_face, tab_manual = st.tabs(["👤 Accesso Rapido", "🔑 Manuale"])
        
        with tab_face:
            if st.button("✨ Entra con Passkey di Test", type="primary"):
                st.session_state.logged_in = True
                st.session_state.email_user = "nicolafronte@icloud.com"
                st.session_state.email_password = "dwhh-jmgx-shmj-ulwa"
                st.session_state.openai_key = "Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA"
                st.rerun()

        with tab_manual:
            manual_email = st.text_input("Email", value="nicolafronte@icloud.com")
            manual_pass = st.text_input("Password App", type="password", value="dwhh-jmgx-shmj-ulwa")
            manual_key = st.text_input("OpenAI Key", type="password", value="Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlbkFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA")
            
            if st.button("Accedi al Sistema", type="primary"):
                if manual_email and manual_pass and manual_key:
                    st.session_state.logged_in = True
                    st.session_state.email_user = manual_email
                    st.session_state.email_password = manual_pass
                    st.session_state.openai_key = manual_key
                    st.rerun()
                else:
                    st.error("Inserisci tutti i campi obbligatori.")
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# SEZIONE 2: DASHBOARD PRINCIPALE
# ==========================================
else:
    # Sidebar di navigazione e profilo
    with st.sidebar:
        st.write(f"👤 **Utente:** {st.session_state.email_user}")
        st.divider()
        if st.button("Disconnetti (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("📊 Dashboard Gestione Email")
    st.markdown("Benvenuto nel tuo pannello di controllo intelligente. Avvia l'analisi per smistare la posta, trovare le comunicazioni importanti ed eliminare lo spam.")

    if st.button("🚀 Avvia Scansione e Pulizia Casella", type="primary"):
        with st.spinner("Connessione al server di posta e analisi IA in corso..."):
            try:
                # Connessione IMAP (es. iCloud / Gmail)
                mail = imaplib.IMAP4_SSL("imap.mail.me.com")
                mail.login(st.session_state.email_user, st.session_state.email_password)
                mail.select("inbox")

                status, messages = mail.search(None, 'UNSEEN')
                
                inbox_emails = []
                important_emails = []
                spam_emails = []

                if status == 'OK' and messages and messages[0]:
                    email_ids = messages[0].split()
                    if email_ids:
                        client = OpenAI(api_key=st.session_state.openai_key)
                        
                        # Analizziamo gli ultimi messaggi non letti (es. ultimi 5)
                        for e_id in email_ids[-5:]:
                            res, msg_data = mail.fetch(e_id, '(RFC822)')
                            for response_part in msg_data:
                                if isinstance(response_part, tuple):
                                    msg = email.message_from_bytes(response_part[1])
                                    subject = str(msg["Subject"] or "Senza oggetto")
                                    sender = str(msg["From"] or "Sconosciuto")
                                    
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

                                    # Prompt strutturato per farsi restituire JSON dall'IA
                                    system_prompt = """
                                    Sei un segretario virtuale intelligente. Analizza l'email e rispondi ESCLUSIVAMENTE in formato JSON con questa struttura esatta:
                                    {
                                        "categoria": "Importante" o "Spam" o "Normale",
                                        "motivazione": "Breve spiegazione del perché",
                                        "azione_consigliata": "Cosa deve fare l'utente"
                                    }
                                    """
                                    user_prompt = f"Mittente: {sender}\nOggetto: {subject}\nTesto:\n{body[:800]}"
                                    
                                    response = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        response_format={ "type": "json_object" },
                                        messages=[
                                            {"role": "system", "content": system_prompt},
                                            {"role": "user", "content": user_prompt}
                                        ]
                                    )
                                    
                                    ai_result = json.loads(response.choices[0].message.content)
                                    
                                    email_item = {
                                        "id": e_id,
                                        "sender": sender,
                                        "subject": subject,
                                        "analysis": ai_result
                                    }

                                    # Smistamento in base alla categoria dell'IA
                                    if ai_result["categoria"] == "Spam":
                                        spam_emails.append(email_item)
                                        # Esempio di automazione: potresti spostare la mail nello spam/cestino via IMAP
                                    elif ai_result["categoria"] == "Importante":
                                        important_emails.append(email_item)
                                    else:
                                        inbox_emails.append(email_item)
                                        
                mail.logout()
                
                # Salviamo i risultati nella sessione per mostrarli nelle tab
                st.session_state.last_inbox = inbox_emails
                st.session_state.last_important = important_emails
                st.session_state.last_spam = spam_emails
                st.success("Scansione completata con successo!")

            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")

    # Se ci sono dati analizzati, mostriamo le sezioni a schede (Tab) moderne
    if "last_important" in st.session_state:
        st.divider()
        
        tab1, tab2, tab3 = st.tabs([
            f"🚨 Importanti ({len(st.session_state.last_important)})", 
            f"📥 Posta Normale ({len(st.session_state.last_inbox)})", 
            f"🗑️ Spam Pulito ({len(st.session_state.last_spam)})"
        ])
        
        with tab1:
            st.subheader("Email che richiedono attenzione immediata")
            if not st.session_state.last_important:
                st.info("Nessuna email importante trovata in questa sessione.")
            for item in st.session_state.last_important:
                with st.container():
                    st.markdown(f"<div class='clean-card'><b>Mittente:</b> {item['sender']}<br><b>Oggetto:</b> {item['subject']}<br><hr style='margin: 10px 0;'>💬 <i>{item['analysis']['motivazione']}</i><br>⚡ <b>Azione:</b> {item['analysis']['azione_consigliata']}</div>", unsafe_allow_html=True)

        with tab2:
            st.subheader("Posta standard")
            if not st.session_state.last_inbox:
                st.info("Nessuna email normale da visualizzare.")
            for item in st.session_state.last_inbox:
                with st.container():
                    st.markdown(f"<div class='clean-card'><b>Mittente:</b> {item['sender']}<br><b>Oggetto:</b> {item['subject']}<br>📝 {item['analysis']['motivazione']}</div>", unsafe_allow_html=True)

        with tab3:
            st.subheader("Email classificate come Spam e filtrate")
            if not st.session_state.last_spam:
                st.info("Nessun messaggio di spam individuato.")
            for item in st.session_state.last_spam:
                with st.container():
                    st.markdown(f"<div class='clean-card' style='border-left: 4px solid #ef4444;'><b>Mittente:</b> {item['sender']}<br><b>Oggetto:</b> {item['subject']}<br>🚫 <b>Motivo blocco:</b> {item['analysis']['motivazione']}</div>", unsafe_allow_html=True)
