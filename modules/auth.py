import streamlit as st
import pandas as pd

USER_KEY = "username"
LOGIN_KEY = "logged_in"

DEMO_ACCOUNTS = [
    {"Kullanıcı Adı": "tuseb", "Parola": "tuseb123"},
    {"Kullanıcı Adı": "user1", "Parola": "user1"},
    {"Kullanıcı Adı": "user2", "Parola": "user123"},
]

def check_auth():
    return st.session_state.get(LOGIN_KEY, False)

def authenticate(username, password):
    return any(
        acc["Kullanıcı Adı"] == username and acc["Parola"] == password
        for acc in DEMO_ACCOUNTS
    )

def login_screen():
    st.image("logo/logo.png", width=150)
    st.title("TKE Somatik Analiz")
    st.subheader("Giriş Yapın")

    user = st.text_input("Kullanıcı Adı")
    pwd = st.text_input("Parola", type="password")

    if st.button("Giriş Yap"):
        if authenticate(user, pwd):
            st.session_state[LOGIN_KEY] = True
            st.session_state[USER_KEY] = user
            st.rerun()
        else:
            st.error("Kullanıcı adı veya parola hatalı.")

    st.markdown("---")
    st.caption("Demo Hesaplar")
    st.dataframe(pd.DataFrame(DEMO_ACCOUNTS), width="stretch", hide_index=True)
