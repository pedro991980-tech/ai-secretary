import streamlit as st
import imaplib
import email
from openai import OpenAI

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="AI Secretary",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Secretary - Dashboard")
st.write("Il tuo assistente email intelligente è online e operativo.")

# I tuoi dati personali inseriti direttamente nel codice
OPENAI_API_KEY = "Sk-proj-_YoFIXvqucspPi-mpJl48E_HpF-h7B6VstS1RxKCju31Ys-92KT1nmRrlz1Nw6KRoJpyg6ZxQWT3BlblurredFJGpqrsNEGkfshJjK7W7vuss3waLFvlGUIHTPEkZ_79qkroKxKu7l_MwfOMPhFR5lPrY04OBauwA"
EMAIL_USER = "nicolafronte@icloud.com"
EMAIL_PASSWORD = "dwhh-jmgx-shmj-ulwa"

# Controllo visivo dello stato delle configurazioni
col1, col2 = st.columns(2)
with col1:
    if OPENAI_API_KEY:
        st.success("🔑 OpenAI API: Configuriata")
    else:
        st.warning("⚠️ OpenAI API: Mancante")

with col2:
    if EMAIL_USER and EMAIL_PASSWORD:
        st.success(f"📧 Email ({EMAIL_USER}): Configurata")
    else:
        st.warning("⚠️ Email: Mancante")

st.divider()

# Sezione interattiva per l'utente
st.subheader("Controllo e Analisi Email")
st.write("Clicca sul pulsante sottostante per connetterti alla casella iCloud e analizzare i nuovi messaggi con l'intelligenza artificiale.")

if st.button("🚀 Avvia controllo email", type="primary"):
    with st.spinner("Connessione alla casella di posta e analisi in corso..."):
        try:
            # Connessione al server IMAP di iCloud
            mail = imaplib.IMAP4_SSL("imap.mail.me.com")
            mail.login(EMAIL_USER, EMAIL_PASSWORD)
            mail.select("inbox")

            # Ricerca delle email non lette
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                st.warning("Errore durante la ricerca delle email.")
            else:
                email_ids = messages[0].split()
                if not email_ids:
                    st.success("Controllo completato: nessuna nuova email da leggere.")
                else:
                    st.info(f"Trovate {len(email_ids)} nuove email da analizzare.")
                    
                    # Inizializzazione del client OpenAI
                    client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    # Analisi delle email trovate (ultime 3)
                    for e_id in email_ids[-3:]:
                        res, msg_data = mail.fetch(e_id, '(RFC822)')
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject = msg["Subject"]
                                sender = msg["From"]
                                
                                # Estrazione del corpo dell'email
                                body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            body = part.get_payload(decode=True).decode(errors='ignore')
                                            break
                                else:
                                    body = msg.get_payload(decode=True).decode(errors='ignore')

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
st.info("L'applicazione è configurata e pronta all'uso.")
