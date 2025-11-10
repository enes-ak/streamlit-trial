import streamlit as st
import pandas as pd
import os
import subprocess
import signal

# ==============================
# ✅ GLOBAL CONSTANTS
# ==============================
APP_TITLE = "TKE Somatic Analyser"
LOGO_PATH = "logo/logo.png"
user_name = "User Name"
password = "Password"
DEMO_ACCOUNTS = [
    {user_name: "tuseb", password: "tuseb123"},
    {user_name: "user1", password: "user1"},
    {user_name: "user2", password: "user123"},
]
pd.DataFrame(DEMO_ACCOUNTS)
DATA_DIR = "data"
VARIANT_TABLE_DIR = os.path.join(DATA_DIR, "variant_table")
STATISTICS_DIR = os.path.join(DATA_DIR, "statistics")

DOCKER_IMAGE = "mypipeline"
DOCKER_MOUNTS = [
    ("/home/enes/Desktop/dbs5_4_dev", "/pipeline/dbs"),
    ("/home/enes/Desktop/denemeler/streamlit-trial/single_sample/data", "/pipeline/data"),
    ("/home/enes/Desktop/denemeler/streamlit-trial/single_sample/config_docker.yaml", "/pipeline/config_docker.yaml"),
    ("/home/enes/Desktop/pipelines/single_sample/.snakemake/conda", "/pipeline/.snakemake/conda"),
    ("/home/enes/Desktop/denemeler/streamlit-trial/single_sample/samples_vcf.csv", "/pipeline/samples_vcf.csv"),
    ("/home/enes/Desktop/denemeler/streamlit-trial/input_files/small_vcf2.vcf", "/pipeline/input_files/small_vcf2.vcf")
]
SNAKEMAKE_CMD = "snakemake -s snakefile_germline_vcf.smk --configfile config_docker.yaml --use-conda --conda-frontend mamba -j12 -c12 -F"

# ==============================
# ✅ HELPER FUNCTIONS
# ==============================
def authenticate(user, pwd):
    return any(acc["User Name"] == user and acc["Password"] == pwd for acc in DEMO_ACCOUNTS)

def login_screen():
    st.title(f"{APP_TITLE} - Login Page")
    user = st.text_input("User Name")
    pwd = st.text_input("Password", type="password")
    if st.button("Giriş Yap"):
        if authenticate(user, pwd):
            st.session_state.update({
                "logged_in": True,
                "username": user,
                "page": "Profile",
                "selected_table": None
            })
            st.rerun()
        else:
            st.error("Kullanıcı adı veya parola hatalı")

    st.markdown("---")
    with st.container():
        st.markdown("### Demo Accounts")
        st.table(pd.DataFrame(DEMO_ACCOUNTS))

def run_docker_pipeline():
    docker_cmd = ["docker", "run", "--rm"] + \
                 sum([["-v", f"{host}:{container}"] for host, container in DOCKER_MOUNTS], []) + \
                 ["--entrypoint", "bash", DOCKER_IMAGE, "-c", SNAKEMAKE_CMD]

    log_box = st.empty()
    process = subprocess.Popen(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    st.session_state["pipeline_process"] = process

    log_text = ""
    for line in process.stdout:
        log_text += line
        log_box.code(log_text, language="bash")

    process.wait()
    if process.returncode == 0:
        st.success("Pipeline finished successfully!")
    else:
        st.error("Pipeline failed! Check logs above.")

def stop_pipeline():
    if "pipeline_process" in st.session_state and st.session_state["pipeline_process"].poll() is None:
        proc = st.session_state["pipeline_process"]
        os.kill(proc.pid, signal.SIGTERM)
        st.session_state["pipeline_process"] = None
        st.warning("Pipeline stopped!")

# ==============================
# ✅ STREAMLIT CONFIG
# ==============================
st.set_page_config(page_title=APP_TITLE, layout="wide")
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ==============================
# ✅ HEADER
# ==============================
header = st.container()
with header:
    col1, col2, col3 = st.columns([1, 9, 1])
    with col1:
        st.image(LOGO_PATH, width=100)
    with col2:
        st.markdown(f"<h2 style='text-align: center; margin-top: 10px;'>{APP_TITLE}</h2>", unsafe_allow_html=True)
    with col3:
        st.write(f"**{st.session_state['username']}**")
        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            st.rerun()

# ==============================
# ✅ SIDEBAR
# ==============================
st.markdown("""
    <style>
        [data-testid="stSidebar"] { min-width: 145px; max-width: 145px; }
        [data-testid="stSidebar"] .block-container { padding-top:1rem; padding-left:0.5rem; padding-right:0.5rem; }
    </style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.session_state["page"] = st.radio("Select", ["Profile", "Results", "New Run"])

# ==============================
# ✅ PAGES
# ==============================
page = st.session_state["page"]

# ---------- PROFILE PAGE ----------
if page == "Profile":
    st.title("Profile Page")
    st.write(f"### Logged-In User: **{st.session_state['username']}**")
    st.markdown("---")
    st.info("User information has been listed in this page.")

# ---------- RESULTS PAGE ----------
elif page == "Results":
    st.title("Run Results")
    tsv_files = [f for f in os.listdir(VARIANT_TABLE_DIR) if f.endswith(".tsv")]
    if not tsv_files:
        st.warning("No project found")
        st.stop()

    col1, col2 = st.columns([0.4,3.6])
    with col1:
        for file in tsv_files:
            if st.button(file):
                st.session_state["selected_table"] = file
    with col2:
        selected = st.session_state.get("selected_table")
        if selected:
            barcode_id = selected.replace(".tsv","")
            stats_path = os.path.join(STATISTICS_DIR, f"{barcode_id}_fraction_coverage.txt")
            st.success(f"Selected Table: **{selected}**")
            df = pd.read_csv(os.path.join(VARIANT_TABLE_DIR, selected), sep="\t")
            st.write(f"Unique Row Size: {len(df)}")

            tabs = st.tabs(["Variant Table", "Statistics"])
            with tabs[0]:
                # st-aggrid yerine basit dataframe gösterimi
                st.dataframe(df, height=700, use_container_width=True)
            with tabs[1]:
                if os.path.exists(stats_path):
                    genome_fraction = pd.read_csv(stats_path, sep="\t")
                    st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
                    st.dataframe(genome_fraction, height=700, use_container_width=True)
                else:
                    st.warning("Statistics file not found")
        else:
            st.info("Select a run")

# ---------- NEW RUN PAGE ----------
elif page == "New Run":
    st.title("Create New Project")
    sample = st.text_input("Sample name")
    vcf_path = st.text_input("VCF file path")
    kit = st.text_input("Kit (e.g., nexome_plus_panel_target)")
    genes = st.text_input("Genes (comma-separated)", value="")
    hpo_terms = st.text_input("HPO Terms", value="-")

    if st.button("Create samples.csv"):
        df = pd.DataFrame([{
            "sample": sample,
            "vcf_path": vcf_path,
            "kit": kit,
            "external_kit": "-",
            "allel_count_db": "input_file_allel_count_germline.tsv",
            "region_allel_number_db": "input_file_region_allel_number_germline.tsv",
            "freq_opt": False,
            "primary_tissue": "-",
            "primary_histology": "-",
            "genes": genes,
            "hpo_terms": hpo_terms
        }])
        df.to_csv("single_sample/samples_vcf.csv", sep="\t", index=False)
        st.success("samples_vcf.csv created successfully.")
        st.write(df)

    if st.button("Run Pipeline"):
        run_docker_pipeline()
    
    if "pipeline_process" in st.session_state and st.session_state["pipeline_process"].poll() is None:
        if st.button("Stop Pipeline"):
            stop_pipeline()
















#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# from st_aggrid import AgGrid, GridOptionsBuilder
# import streamlit as st
# import pandas as pd
# import os
# import subprocess
# import time
# import signal

# # -----------------------------
# # Demo kullanıcı bilgileri
# # -----------------------------
# DEMO_ACCOUNTS = [
#     {"user": "tuseb", "pass": "tuseb123"},
#     {"user": "user1", "pass": "user1"},
#     {"user": "user2", "pass": "user123"},
# ]

# # Kullanıcı doğrulama fonksiyonu
# def authenticate(user, pwd):
#     for acc in DEMO_ACCOUNTS:
#         if acc["user"] == user and acc["pass"] == pwd:
#             return True
#     return False


# # -----------------------------
# # Login ekranı
# # -----------------------------
# def login_screen():
#     st.title("TKE Somatic Analyser - Login Page")

#     user = st.text_input("User Name")
#     pwd = st.text_input("Password", type="password")

#     if st.button("Giriş Yap"):
#         if authenticate(user, pwd):
#             st.session_state["logged_in"] = True
#             st.session_state["username"] = user
#             st.session_state["page"] = "Profile"
#             st.session_state["selected_table"] = None
#             st.rerun()
#         else:
#             st.error("Kullanıcı adı veya parola hatalı")

#     st.markdown("---")
#     demo_box = st.container(border=True)
#     with demo_box:
#         st.markdown("### Demo Accounts")
#         st.table(pd.DataFrame(DEMO_ACCOUNTS))


# # -----------------------------
# # Page config
# # -----------------------------
# st.set_page_config(page_title="TKE Somatic Analyser", layout="wide")

# # -----------------------------
# # Login kontrol
# # -----------------------------
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False

# if not st.session_state["logged_in"]:
#     login_screen()
#     st.stop()


# # ======================================================
# # ✅ ÜST HEADER
# # ======================================================
# header = st.container()
# with header:
#     col1, col2, col3 = st.columns([1, 9, 1])

#     with col1:
#         st.image("logo/logo.png", width=100)

#     with col2:
#         st.markdown(
#             """
#             <h2 style='text-align: center; margin-top: 10px;'>
#             TKE Somatic Analyser
#             </h2>
#             """,
#             unsafe_allow_html=True
#         )

#     with col3:
#         st.write(f"**{st.session_state['username']}**")
#         if st.button("Log Out"):
#             st.session_state["logged_in"] = False
#             st.rerun()


# # ======================================================
# # ✅ SOL MENÜ
# # ======================================================

# st.markdown("""
#     <style>
#         /* Sidebar genişliğini küçültme */
#         [data-testid="stSidebar"] {
#             min-width: 145px;
#             max-width: 145px;
#         }

#         /* Sidebar içindeki widget padding’i azaltma */
#         [data-testid="stSidebar"] .block-container {
#             padding-top: 1rem;
#             padding-left: 0.5rem;
#             padding-right: 0.5rem;
#         }
#     </style>
# """, unsafe_allow_html=True)
# with st.sidebar:
#     menu = st.radio("Select", ["Profile", "Results", "New Run"])
# st.session_state["page"] = menu

# # ======================================================
# # ✅ PROFIL SAYFASI
# # ======================================================
# if st.session_state["page"] == "Profile":
#     st.title("Profile Page")

#     st.write("### Logged-In User:")
#     st.write(f"**{st.session_state['username']}**")

#     st.markdown("---")
#     st.info("User information has been listed in this page.")


# # ======================================================
# # ✅ RUN SAYFASI – Projeler + Tablo Görüntüleme
# # ======================================================
# if st.session_state["page"] == "Results":
#     st.title("Run")
#     st.write("### Run Results")

#     # data/ klasöründeki tüm .tsv dosyalarını listele
#     tsv_files = [f for f in os.listdir("data/variant_table") if f.endswith(".tsv")]

#     if len(tsv_files) == 0:
#         st.warning("No project found")
#         st.stop()

#     col1, col2 = st.columns([0.4,3.6])

#     with col1:
#         for file in tsv_files:
#             if st.button(file):
#                 st.session_state["selected_table"] = file

#     with col2:
#         if st.session_state.get("selected_table"):
#             selected = st.session_state["selected_table"]
#             barcode_id = selected.replace(".tsv", "")
#             stats_path = f"data/statistics/{barcode_id}_fraction_coverage.txt"
#             st.success(f"Selected Table: **{selected}**")
#             df = pd.read_csv(f"data/variant_table/{selected}", sep="\t")
#             st.write(f"Unique Row Size: {len(df)}")
#             tabs = st.tabs(["Variant Table", "Statistics"])
            
#             # ✅ Variant Table
#             with tabs[0]:
#                 gb = GridOptionsBuilder.from_dataframe(df)
#                 gb.configure_default_column(
#                     filterable=True,  # tüm kolonlarda filtre aktif
#                     sortable=True,
#                     resizable=True,
#                     minWidth=150
#                 )
#                 # Sadece Main.variant_class için text search bar
#                 filter_columns = ["Main.variant_class", "Main.gene_symbol"]
                
#                 for col in filter_columns:
#                     gb.configure_column(col, filter="agTextColumnFilter", width=150)
#                 gridOptions = gb.build()
            
#                 AgGrid(
#                     df,
#                     gridOptions=gridOptions,
#                     height=700,
#                     enable_enterprise_modules=False,
#                     theme="alpine",
#                     fit_columns_on_grid_load=False
#                 )
#             # ✅ Statistics Tab
#             with tabs[1]:
#                 if os.path.exists(stats_path):
#                     genome_fraction = pd.read_csv(stats_path, sep="\t")
#                     st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
#                     st.dataframe(
#                         genome_fraction, height=700, use_container_width=True)
#                 else:
#                     st.warning("Statistics file not found")

#         else:
#             st.info("Select a run")
            

# elif st.session_state["page"] == "New Run":
#     st.title("Create New Project")

#     # Kullanıcıdan alınacak girdiler
#     sample = st.text_input("Sample name")
#     vcf_path = st.text_input("VCF file path")
#     kit = st.text_input("Kit (ör. nexome_plus_panel_target)")
#     genes = st.text_input("Genes (comma-separated)", value="")
#     hpo_terms = st.text_input("HPO Terms", value="-")

#     # Otomatik alanlar
#     if st.button("Create samples.csv"):
#         df = pd.DataFrame([{
#             "sample": sample,
#             "vcf_path": vcf_path,
#             "kit": kit,
#             "external_kit": "-",
#             "allel_count_db": "input_file_allel_count_germline.tsv",
#             "region_allel_number_db": "input_file_region_allel_number_germline.tsv",
#             "freq_opt": False,
#             "primary_tissue": "-",
#             "primary_histology": "-",
#             "genes": genes,
#             "hpo_terms": hpo_terms
#         }])
#         # os.makedirs("data", exist_ok=True)
#         df.to_csv("single_sample/samples_vcf.csv", sep="\t", index=False)
#         st.success("samples_vcf.csv created successfully.")
#         st.write(df)

#     if st.button("Run Pipeline"):
#         st.info("Pipeline started... This may take a while!")
        

#         docker_cmd = [
#             "docker", "run", "--rm",
#             "-v", "/home/enes/Desktop/dbs5_4_dev:/pipeline/dbs",
#             "-v", "/home/enes/Desktop/denemeler/streamlit-trial/single_sample/data:/pipeline/data",
#             "-v", "/home/enes/Desktop/denemeler/streamlit-trial/single_sample/config_docker.yaml:/pipeline/config_docker.yaml",
#             "-v", "/home/enes/Desktop/pipelines/single_sample/.snakemake/conda:/pipeline/.snakemake/conda",
#             "-v", "/home/enes/Desktop/denemeler/streamlit-trial/single_sample/samples_vcf.csv:/pipeline/samples_vcf.csv",
#             "-v", "/home/enes/Desktop/denemeler/streamlit-trial/input_files/small_vcf2.vcf:/pipeline/input_files/small_vcf2.vcf",
#             "--entrypoint", "bash",
#             "mypipeline",
#             "-c",
#             "snakemake -s snakefile_germline_vcf.smk --configfile config_docker.yaml --use-conda --conda-frontend mamba -j12 -c12 -F"
#         ]
        
#         try:
#             log_box = st.empty()   # sürekli güncellenecek alan
#             process = subprocess.Popen(
#                 docker_cmd,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.STDOUT,
#                 text=True,
#                 bufsize=1
#             )

#             log_text = ""  # tüm loglar burada birikecek

#             # satır satır log oku ve ekrana yaz
#             for line in process.stdout:
#                 log_text += line
#                 log_box.code(log_text, language="bash")

#             process.wait()

#             if process.returncode == 0:
#                 st.success("Pipeline finished successfully!")
#             else:
#                 st.error("Pipeline failed! Check logs above.")

#         except Exception as e:
#             st.error("Pipeline crashed unexpectedly!")
#             st.exception(e)
