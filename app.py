import streamlit as st
import pandas as pd
import os
import subprocess
import time


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
    st.title("TUSEB Genome Analyser - Login Page")

    user = st.text_input("User Name")
    pwd = st.text_input("Password", type="password")

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
        st.markdown("### Demo Accounts")
        st.table(pd.DataFrame(DEMO_ACCOUNTS))


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="TUSEB Genome Analyser", layout="wide")

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
    col1, col2, col3 = st.columns([1, 9, 1])

    with col1:
        st.image("logo/logo.png", width=100)

    with col2:
        st.markdown(
            """
            <h2 style='text-align: center; margin-top: 10px;'>
            TUSEB Genome Analyser
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
            min-width: 145px;
            max-width: 145px;
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
    menu = st.radio("Select", ["Profile", "Results", "New Run"])
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
if st.session_state["page"] == "Results":
    st.title("Run")
    st.write("### Run Results")

    # data/ klasöründeki tüm .tsv dosyalarını listele
    tsv_files = [f for f in os.listdir("data/variant_table") if f.endswith(".tsv")]

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
            barcode_id = selected.replace(".tsv", "")
            stats_path = f"data/statistics/{barcode_id}_fraction_coverage.txt"
            st.success(f"Selected Table: **{selected}**")
            df = pd.read_csv(f"data/variant_table/{selected}", sep="\t")
            st.write(f"Unique Row Size: {len(df)}")
            tabs = st.tabs(["Variant Table", "Statistics"])
            
            # ✅ Variant Table
            with tabs[0]:
                st.dataframe(df, height=700, use_container_width=True)
            
            # ✅ Statistics Tab
            with tabs[1]:
                if os.path.exists(stats_path):
                    genome_fraction = pd.read_csv(stats_path, sep="\t")
                    st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
                    st.dataframe(
                        genome_fraction, height=700, use_container_width=True)
                else:
                    st.warning("Statistics file not found")

        else:
            st.info("Select a run")
            

elif st.session_state["page"] == "New Run":
    st.title("Create New Project")

    project_name = st.text_input("Project Name")
    input_path = st.text_input("Input VCF Path")
    kit = st.selectbox("Select Kit", ["WES", "CES", "WGS"])

    outdir = f"projects/{project_name}"

    if st.button("Run"):
        if not project_name or not input_path:
            st.error("Please provide project name and input path.")
            st.stop()

        st.info("Pipeline started... this may take time.")
        st.write("Running Snakemake...")

        SNAKEMAKE = "env/snakemake/bin/snakemake"

        snake_cmd = [
            SNAKEMAKE,
            "-s", "single_sample/snakefile_germline_vcf.smk",
            "-j", "16",
            "--configfile", "single_sample/config.yaml",
            f"input={input_path}",
            f"kit={kit}",
            f"outdir={outdir}"
        ]

        process = subprocess.Popen(
            snake_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # ✅ CANLI LOG GÖSTERİMİ
        log_box = st.empty()
        full_log = ""

        # stdout satırlarını canlı aktar
        for line in process.stdout:
            full_log += line
            log_box.text(full_log)

        # pipeline bittiyse stderr’i ekle
        stderr_output = process.stderr.read()
        if stderr_output:
            full_log += "\n--- STDERR OUTPUT ---\n" + stderr_output
            log_box.text(full_log)

        return_code = process.wait()

        if return_code == 0:
            st.success("Pipeline finished successfully!")
            st.session_state["last_project"] = project_name
        else:
            st.error("Pipeline failed! Check log above.")
            st.stop()
