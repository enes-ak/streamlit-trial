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
            st.session_state["page"] = "Profil"
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
# ✅ SOL FRAME (SIDEBAR)
# ======================================================
# st.sidebar.title("Men")

if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()

menu = st.sidebar.radio("Select", ["Profile", "Run"])
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
# ✅ RUN SAYFASI — TIKLANABİLİR TABLO LİSTESİ
# ======================================================
if st.session_state["page"] == "Run":
    st.title("Run")

    st.write("### Run Results")

    # data/ klasöründeki tüm .tsv dosyalarını listele
    tsv_files = [f for f in os.listdir("data") if f.endswith(".tsv")]

    if len(tsv_files) == 0:
        st.warning("No project found")
        st.stop()

    # Sol sütunda tablolar listesi
    col1, col2 = st.columns([1, 3])

    with col1:
        # st.write("#### Dosya Listesi")
        for file in tsv_files:
            if st.button(file):  
                st.session_state["selected_table"] = file

    # Sağ tarafta seçilen tablo görüntülenecek
    with col2:
        if st.session_state.get("selected_table"):
            selected = st.session_state["selected_table"]

            st.success(f"Selected Table: **{selected}**")

            # Sekmeler: Variant Table + Statistics
            tabs = st.tabs(["Variant Table", "Statistics"])

            with tabs[0]:
                df = pd.read_csv(f"data/{selected}", sep="\t")
                st.dataframe(df, width="stretch", height=700)

            with tabs[1]:
                stats_path = "data/genome_fraction_coverage.txt"
                if os.path.exists(stats_path):
                    genome_fraction = pd.read_csv(stats_path, sep="\t")
                    st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
                    st.dataframe(genome_fraction, width="stretch", height=700)
                else:
                    st.warning("Statistics file not found")
        else:
            st.info("Select a run")
