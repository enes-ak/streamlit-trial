import streamlit as st

def profile_page():
    st.title("👤 Profil")
    st.info(f"Giriş yapan kullanıcı: **{st.session_state['username']}**")
    st.markdown("Bu sayfada kullanıcı bilgileri görüntülenir.")
