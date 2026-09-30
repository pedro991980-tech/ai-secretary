import streamlit as st
import imaplib
import email
from openai import OpenAI
import os

# 1. Configurazione della pagina
st.set_page_config(
    page_title="AI Secretary",
    page_icon="🤖",
    layout="centered"
)

# 2. Personalizzazione Tipografica (Caratteri ingranditi del 150%)
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 1.5rem !important;
    }
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Sidebar per Branding (Logo) e Credenziali Dinamiche (BYOK)
st.sidebar.title("🤖 AI Secretary")

# Ricerca e caricamento del logo dalla cartella locale del progetto
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=120)
else:
    # Cerca un'immagine generica di logo nella cartella corrente se il nome è differente
    for filename in os.listdir("."):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and 'logo' in filename.lower():
            st.sidebar.image(filename, width=120)
            break

st.sidebar.subheader("Accesso Personale")
user_email = st.sidebar.text_input("Email iCloud", placeholder="tuamail@icloud.com")
user_password = st.sidebar.text_input("Password per App", type="password", placeholder="xxxx-xxxx-xxxx-xxxx")
user_openai_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...")

st.title("🤖 AI Secretary - Dashboard")

# Controllo se l'utente ha inserito tutti i dati necessari
if not user_email or not user_password or not user_openai_key:
    st.warning("⚠️ Inserisci la tua email, la password specifica per app e la tua chiave OpenAI nella barra laterale a sinistra per attivare l'assistente.")
    st.stop()

st.success("✅ Credenziali inserite con successo. Avvio analisi automatica...")
st.divider()

# 4. Automazione Completa (Zero-Click Processing)
st.subheader("📬 Analisi Posta in Arrivo")

with st.spinner("Connessione sicura al server IMAP e analisi in corso..."):
    try:
        # Connessione al server IMAP di iCloud
        mail = imaplib.IMAP4_SSL("imap.mail.me.com")
        mail.login(user_email, user_password)
        mail.select("inbox")

        # Ricerca delle email non lette
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            st.error("Errore durante la ricerca delle email sul server.")
        else:
            raw_messages = messages[0]
            if not raw_messages:
                st.info("Nessuna nuova email non letta trovata nella casella di posta.")
            else:
                email_ids = raw_messages.split()
                if not email_ids:
                    st.info("Nessuna nuova email non letta trovata nella casella di posta.")
                else:
                    st.info(f"Trovate {len(email_ids)} nuove email da analizzare.")
                    
                    # Inizializzazione del client OpenAI con la chiave personale dell'utente
                    client = OpenAI(api_key=user_openai_key)
                    
                    # Analisi delle email trovate (ultime 3)
                    for e_id in email_ids[-3:]:
                        res, msg_data = mail.fetch(e_id, '(RFC822)')
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject = msg["Subject"] or "Senza oggetto"
                                sender = msg["From"] or "Mittente sconosciuto"
                                
                                # Estrazione del corpo dell'email
                                body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            try:
                                                body = part.get_payload(decode=True).decode(errors='ignore')
                                            except:
                                                pass
                                            break
                                else:
                                    try:
                                        body = msg.get_payload(decode=True).decode(errors='ignore')
                                    except:
                                        pass

                                # Richiesta a OpenAI per analizzare l'email
                                prompt = f"Mittente: {sender}\nOggetto: {subject}\nTesto:\n{body[:1000]}"
                                
                                response = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[
                                        {"role": "system", "content": "Sei un segretario efficiente. Riassumi questa email in modo chiaro e indica se richiede un'azione urgente."},
                                        {"role": "user", "content": prompt}
                                    ]
                                )
                                
                                analysis = response.choices[0].message.content
                                
                                # Mostra il risultato nell'interfaccia web
                                with st.expander(f"📩 Da: {sender} - {subject}"):
                                    st.write(analysis)
                                    
        mail.logout()
        
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'esecuzione: {e}")

st.divider()
st.subheader("📜 Stato del sistema")
st.info("L'applicazione è operativa in modalità multiutente e autonoma.")
