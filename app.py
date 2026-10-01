import streamlit as st
import imaplib
import email
from email.header import decode_header
from openai import OpenAI
import os

# 1. Configurazione della pagina
st.set_page_config(
    page_title="AI Secretary Pro",
    page_icon="🤖",
    layout="centered"
)

# 2. UI/UX Moderna, Accessibile e di Classe (Stile SaaS Enterprise)
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
        background: rgba(255, 255, 255, 0.9);
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

# Funzione di supporto sicura per decodificare gli header delle email
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

# 3. Sidebar Professionale con Branding e Configurazione Universale (BYOK)
with st.sidebar:
    # Gestione sicura del logo aziendale / icona app
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    else:
        # Fallback intelligente se il file ha un nome differente nella directory
        found_logo = False
        for filename in os.listdir("."):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and 'logo' in filename.lower():
                st.image(filename, width=140)
                found_logo = True
                break
        if not found_logo:
            st.markdown("### 🤖 AI Secretary")
            
    st.markdown("---")
    st.subheader("Configurazione Account")
    
    # Input isolati e protetti nella sessione
    user_email = st.text_input("Indirizzo Email", placeholder="nome@dominio.com")
    user_password = st.text_input("Password per App", type="password", placeholder="Genera password specifica")
    user_openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    st.caption("🔒 Crittografia TLS/SSL attiva. Le credenziali non vengono mai memorizzate in modo permanente sul server.")

# Interfaccia Principale
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.title("🤖 AI Secretary - Dashboard")
st.markdown("<p style='color: #64748b;'>Assistente di posta intelligente, sicuro e multi-provider.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Validazione dei prerequisiti di sicurezza (Zero-Trust configuration check)
if not user_email or not user_password or not user_openai_key:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.info("👋 **Benvenuto!** Per iniziare, inserisci i dati della tua casella di posta e la tua chiave OpenAI nella barra laterale a sinistra.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. Connessione IMAP Universale & Elaborazione Sicura
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("📬 Analisi Posta in Arrivo")

if st.button("🚀 Avvia Scansione Intelligente", type="primary"):
    with st.spinner("Connessione sicura al server di posta in corso..."):
        try:
            # Rilevamento automatico del server IMAP in base al dominio dell'utente (Supporto Universale)
            email_lower = user_email.strip().lower()
            if "gmail.com" in email_lower:
                imap_server = "imap.gmail.com"
            elif "icloud.com" in email_lower or "me.com" in email_lower:
                imap_server = "imap.mail.me.com"
            elif "outlook.com" in email_lower or "hotmail.com" in email_lower or "live.com" in email_lower:
                imap_server = "imap-mail.outlook.com"
            else:
                imap_server = "imap.mail.me.com" # Fallback sicuro

            # Connessione SSL blindata
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(user_email.strip(), user_password.strip())
            mail.select("inbox")

            # Ricerca dei messaggi non letti
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                st.error("Impossibile recuperare i messaggi dal server IMAP.")
            else:
                raw_messages = messages[0]
                if not raw_messages:
                    st.success("Casella di posta pulita: nessuna nuova email da leggere.")
                else:
                    email_ids = raw_messages.split()
                    if not email_ids:
                        st.success("Casella di posta pulita: nessuna nuova email da leggere.")
                    else:
                        st.info(f"Trovate {len(email_ids)} nuove email da analizzare.")
                        
                        # Inizializzazione client OpenAI isolato per sessione
                        client = OpenAI(api_key=user_openai_key.strip())
                        
                        # Analisi delle ultime email non lette (limitate a 3 per performance e stabilità)
                        for e_id in email_ids[-3:]:
                            res, msg_data = mail.fetch(e_id, '(RFC822)')
                            for response_part in msg_data:
                                if isinstance(response_part, tuple):
                                    msg = email.message_from_bytes(response_part[1])
                                    subject = decode_email_header(msg["Subject"])
                                    sender = decode_email_header(msg["From"])
                                    
                                    # Estrazione sicura del corpo dell'email
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

                                    # Prompt di sistema per l'intelligenza artificiale
                                    prompt = f"Mittente: {sender}\nOggetto: {subject}\nTesto:\n{body[:1000]}"
                                    
                                    response = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "system", "content": "Sei un segretario esecutivo efficiente. Riassumi questa email in modo chiaro, conciso e indica immediatamente se richiede un'azione urgente."},
                                            {"role": "user", "content": prompt}
                                        ]
                                    )
                                    
                                    analysis = response.choices[0].message.content
                                    
                                    # Rendering pulito ed elegante dei risultati
                                    with st.expander(f"📩 Da: {sender} — {subject}"):
                                        st.markdown(analysis)
                                        
            mail.logout()
            
        except Exception as e:
            st.error(f"Errore di autenticazione o connessione IMAP: {e}")

st.markdown("</div>", unsafe_allow_html=True)
