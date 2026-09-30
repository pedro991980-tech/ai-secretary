import streamlit as st
import os

st.set_page_config(page_title="AI Secretary", page_icon="🤖")

st.title("🤖 AI Secretary - Dashboard")
st.write("Benvenuto nella versione web del tuo assistente email intelligente.")

# Gestione sicura delle credenziali tramite i Secrets di Streamlit Cloud
try:
    openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    openai_key = os.environ.get("OPENAI_API_KEY", "")

# Sezione interattiva
st.subheader("Controllo manuale")
if st.button("🚀 Avvia controllo email"):
    with st.spinner("L'assistente sta analizzando le email in arrivo..."):
        # -> Inserisci qui la chiamata alla funzione principale del tuo script ai.secretary.py <-
        st.success("Analisi completata con successo!")

st.divider()
st.subheader("📜 Log di sistema")
st.text("L'applicazione è in ascolto e pronta all'uso.")