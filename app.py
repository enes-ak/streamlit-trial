import streamlit as st
import pandas as pd
import os

# -----------------------------
# Demo kullanıcı bilgileri
# -----------------------------
DEMO_ACCOUNTS = [
    {"user": "tuseb", "pass": "tuseb123"},
    {"user": "user1", "pass": "user123"},
    {"user": "user2", "pass": "user123"},
]

# Kullanıcı doğrulama fonksiyonu
def authenticate(user, pwd):
    for acc in DEMO_ACCOUNTS:
        if acc["user"] == user and acc["pass"] == pwd:
            return True
    return False


# -----------------------------
# Login ekranı
# -----------------------------
def login_screen():
    st.title("TUSEB GENOME ANALYSER - Login Page")

    user = st.text_input("Kullanıcı Adı")
    pwd = st.text_input("Parola", type="password")

    if st.button("Giriş Yap"):
        if authenticate(user, pwd):
            st.session_state["logged_in"] = True
            st.session_state["username"] = user
            st.session_state["page"] = "Profile"
            st.session_state["selected_table"] = None
            st.rerun()
        else:
            st.error("Kullanıcı adı veya parola hatalı")

    st.markdown("---")
    demo_box = st.container(border=True)
    with demo_box:
        st.markdown("### Demo Hesaplar")
        st.table(pd.DataFrame(DEMO_ACCOUNTS))


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="TUSEB GENOME ANALYSER", layout="wide")

# -----------------------------
# Login kontrol
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_screen()
    st.stop()


# ======================================================
# ✅ ÜST HEADER
# ======================================================
header = st.container()
with header:
    col1, col2, col3 = st.columns([1, 6, 2])

    with col1:
        st.image("logo/logo.png", width=90)

    with col2:
        st.markdown(
            """
            <h2 style='text-align: center; margin-top: 10px;'>
            TUSEB GENOME ANALYSER
            </h2>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.write(f"**{st.session_state['username']}**")
        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            st.rerun()


# ======================================================
# ✅ SOL MENÜ
# ======================================================

st.markdown("""
    <style>
        /* Sidebar genişliğini küçültme */
        [data-testid="stSidebar"] {
            min-width: 130px;
            max-width: 130px;
        }

        /* Sidebar içindeki widget padding’i azaltma */
        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)
with st.sidebar:
    menu = st.radio("Select", ["Profile", "Run"])
st.session_state["page"] = menu

# ======================================================
# ✅ PROFIL SAYFASI
# ======================================================
if st.session_state["page"] == "Profile":
    st.title("Profile Page")

    st.write("### Logged-In User:")
    st.write(f"**{st.session_state['username']}**")

    st.markdown("---")
    st.info("User information has been listed in this page.")


# ======================================================
# ✅ RUN SAYFASI – Projeler + Tablo Görüntüleme
# ======================================================
if st.session_state["page"] == "Run":
    st.title("Run")
    st.write("### Run Results")

    # data/ klasöründeki tüm .tsv dosyalarını listele
    tsv_files = [f for f in os.listdir("data") if f.endswith(".tsv")]

    if len(tsv_files) == 0:
        st.warning("No project found")
        st.stop()

    col1, col2 = st.columns([0.4,3.6])

    with col1:
        for file in tsv_files:
            if st.button(file):
                st.session_state["selected_table"] = file

    with col2:
        if st.session_state.get("selected_table"):
            selected = st.session_state["selected_table"]
            st.success(f"Selected Table: **{selected}**")

            tabs = st.tabs(["Variant Table", "Statistics"])

            # ✅ Variant Table
            with tabs[0]:
                df = pd.read_csv(f"data/{selected}", sep="\t")
                st.dataframe(df, height=700, use_container_width=True)

            # ✅ Statistics Tab
            with tabs[1]:
                stats_path = "data/genome_fraction_coverage.txt"
                if os.path.exists(stats_path):
                    genome_fraction = pd.read_csv(stats_path, sep="\t")
                    st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
                    st.dataframe(
                        genome_fraction, height=700, use_container_width=True
                    )
                else:
                    st.warning("Statistics file not found")

        else:
            st.info("Select a run")
