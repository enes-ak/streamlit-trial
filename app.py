import streamlit as st
from modules.auth import login_screen, check_auth
from modules.profile_page import profile_page
from modules.results_page import results_page
from modules.new_run_page import new_run_page
from modules.ui_styles import load_styles

st.set_page_config(page_title="TKE Somatik Analiz", layout="wide")
load_styles()
st.set_page_config(page_title="TKE Somatik Analiz", layout="wide")
load_styles()


st.markdown("""
<style>
/* Sidebar container'ı flex column yapıyoruz */
section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    height: 100%;
}

/* Menü üstte, logout altta */
.sidebar-top {
    flex: 1 1 auto;
}
.sidebar-bottom {
    flex-shrink: 0;
    padding-top: 360px;
}
</style>
""", unsafe_allow_html=True)

# Login kontrolü
if not check_auth():
    login_screen()
    st.stop()

with st.sidebar:

    # --- TOP (logo + menu) ---
    st.markdown('<div class="sidebar-top">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>TKE - Somatik Analiz Platformu</h3>", 
            unsafe_allow_html=True)
    st.image("logo/logo.png", width=160)

    menu = st.radio(
        "Menü",
        ["👤 Profil", "📊 Sonuçlar", "⚙️ Yeni Çalışma"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTTOM (logout + version) ---
    st.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("Çıkış Yap", width="stretch"):
        st.session_state.clear()
        st.rerun()

    st.markdown(
        "<p style='font-size:13px; color:gray; text-align:center'>v0.1</p>",
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)



# Sayfalar
if menu == "👤 Profil":
    profile_page()

elif menu == "📊 Sonuçlar":
    results_page()

elif menu == "⚙️ Yeni Çalışma":
    new_run_page()
