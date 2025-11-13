import streamlit as st
import pandas as pd
import os
import subprocess
import signal

# ==============================
# ✅ GLOBAL CONSTANTS
# ==============================
APP_TITLE = "TKE Somatik Analiz Uygulaması"
LOGO_PATH = "logo/logo.png"
MASSIVE_BIOINFO_LOGO_PATH = "logo/massive_bioinformatics_logo.png"
RETURN_FILES_DIR = "single_sample/data/return_files"
USER_NAME = "Kullanıcı Adı"
PASSWORD = "Parola"

DEMO_ACCOUNTS = [
    {USER_NAME: "tuseb", PASSWORD: "tuseb123"},
    {USER_NAME: "user1", PASSWORD: "user1"},
    {USER_NAME: "user2", PASSWORD: "user123"},
]

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
    ("/home/enes/Desktop/denemeler/streamlit-trial/input_files", "/pipeline/input_files"),
]

# ("/home/enes/Desktop/denemeler/streamlit-trial/input_files/small_vcf2.vcf", "/pipeline/input_files/small_vcf2.vcf"),
SNAKEMAKE_CMD = (
    "snakemake -s snakefile_germline_vcf.smk --configfile config_docker.yaml "
    "--use-conda --conda-frontend mamba -j12 -c12 -F"
)

# ==============================
# ✅ PAGE SETUP
# ==============================
st.set_page_config(page_title=APP_TITLE, layout="wide")

# ==============================
# 🎨 CUSTOM STYLES
# ==============================
st.markdown("""
<style>
    body { background-color: #f7f9fb; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #1f4e79; }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 18px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #125a8a;
        transform: scale(1.02);
    }
    section[data-testid="stSidebar"] {
        background-color: #ecf2f7;
        border-right: 1px solid #d0d8e0;
    }
    [data-testid="stSidebarNav"] span { color: #1f4e79 !important; }
    [data-testid="stRadio"] > div > label {
        background-color: transparent;
        padding: 6px 10px;
        border-radius: 5px;
        transition: 0.2s;
    }
    [data-testid="stRadio"] > div > label:hover {
        background-color: #dbe8f0;
    }
    pre, code, div[data-testid="stCodeBlock"] {
        width: 100% !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# ✅ HELPER FUNCTIONS
# ==============================
def authenticate(user, pwd):
    return any(acc[USER_NAME] == user and acc[PASSWORD] == pwd for acc in DEMO_ACCOUNTS)

def login_screen():
    st.image(LOGO_PATH, width=150)
    st.title(APP_TITLE)
    st.subheader("Giriş Ekranı")

    user = st.text_input("Kullanıcı Adı")
    pwd = st.text_input("Parola", type="password")

    if st.button("Giriş Yap"):
        if authenticate(user, pwd):
            st.session_state.update({
                "logged_in": True,
                "username": user,
                "page": "Profil",
                "selected_table": None
            })
            st.rerun()
        else:
            st.error("Kullanıcı adı veya parola hatalı.")

    st.markdown("---")

    st.caption("Demo Hesaplar")
    st.dataframe(pd.DataFrame(DEMO_ACCOUNTS), width="stretch", hide_index=True)

    st.markdown(
        """
        <div style="
            background-color:#ecf2f7;
            border-radius:10px;
            padding:15px 20px;
            margin-top:15px;
            border:1px solid #d0d8e0;
        ">
        <h4 style="color:#1f4e79; margin-bottom:5px;">Uygulama Hakkında</h4>
        <p style="color:#333; font-size:15px; line-height:1.5;">
        Bu uygulama, somatik varyant analiz süreçlerini kolaylaştırmak amacıyla geliştirilmiştir.
        Kullanıcı dostu arayüzü sayesinde, genomik verilerin analizini hızlı ve etkili bir şekilde gerçekleştirmenizi sağlar.
        </p>
        <p style="font-size:14px; color:#1f4e79; font-style:italic; margin-top:10px;">
        Massive Bioinformatics Ar-Ge Teknolojileri tarafından geliştirilmiştir.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def run_docker_pipeline():
    docker_cmd = ["docker", "run", "--rm"] + \
                 sum([["-v", f"{host}:{container}"] for host, container in DOCKER_MOUNTS], []) + \
                 ["--entrypoint", "bash", DOCKER_IMAGE, "-c", SNAKEMAKE_CMD]

    st.markdown("### Pipeline Çalışıyor...")

    process = subprocess.Popen(
        docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    st.session_state["pipeline_process"] = process

    log_box = st.empty()

    log_text = ""
    log_container_style = """
    <div style="
        background-color: #f1f5f9;
        color: #1e293b;
        font-family: monospace;
        padding: 12px;
        border-radius: 8px;
        height: 600px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.4;
        font-size: 13px;
        border: 1px solid #cbd5e1;
        width: 100%;
        margin: auto;
    ">
    {content}
    </div>
    """

    for line in process.stdout:
        log_text += line
        # Log kutusunu sabit yükseklikte ve iç kaydırmalı göster
        log_box.markdown(log_container_style.format(content=log_text.replace("<", "&lt;").replace(">", "&gt;")), unsafe_allow_html=True)


    process.wait()
    if process.returncode == 0:
        st.success("✅ Pipeline başarıyla tamamlandı.")

        # Bilgilendirici mesaj kutusu
        st.markdown("""
        <div style='background-color:#eaf5ea; padding:15px; border-radius:10px; border:1px solid #b7dfb9;'>
            <h4>📊 Analiz tamamlandı!</h4>
            <p>
            Analiz sonuçları başarıyla oluşturuldu. 
            <br><br>
            Sonuçlara erişmek için sol menüde yer alan <b>"📊 Sonuçlar"</b> sekmesine gidin 
            ve ilgili örneği listeden seçin.
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ Pipeline hata ile sonlandı. Logları kontrol edin.")

def stop_pipeline():
    if "pipeline_process" in st.session_state and st.session_state["pipeline_process"].poll() is None:
        proc = st.session_state["pipeline_process"]
        os.kill(proc.pid, signal.SIGTERM)
        st.session_state["pipeline_process"] = None
        st.warning("⚠️ Pipeline kullanıcı tarafından durduruldu.")

# ==============================
# ✅ LOGIN CONTROL
# ==============================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ==============================
# ✅ HEADER
# ==============================
col1, col2, col3 = st.columns([1, 8, 1])
with col1:
    st.image(LOGO_PATH, width=70)
with col2:
    st.markdown(f"<h2 style='text-align: center; color:#1f4e79;'>{APP_TITLE}</h2>", unsafe_allow_html=True)
with col3:
    st.write(f"**{st.session_state['username']}**")
    if st.button("Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==============================
# ✅ SIDEBAR
# ==============================
st.sidebar.markdown("### 📂 Menü")
menu = st.sidebar.radio(
    "Sayfa Seçiniz:",
    ["👤 Profil", "📊 Sonuçlar", "⚙️ Yeni Çalışma"],
    label_visibility="collapsed"
)
page = menu.split(" ", 1)[1]



# ==============================
# ✅ PROFILE PAGE
# ==============================
if page == "Profil":
    st.title("👤 Profil Sayfası")
    st.info(f"Giriş yapan kullanıcı: **{st.session_state['username']}**")
    st.markdown("Bu sayfada kullanıcı bilgileri görüntülenir.")

# ==============================
# ✅ RESULTS PAGE
# ==============================
elif page == "Sonuçlar":
    st.title("📊 Analiz Sonuçları")

    if not os.path.exists(RETURN_FILES_DIR):
        st.warning("Sonuç bulunamadı.")
        st.stop()

    tsv_files = [f for f in os.listdir(RETURN_FILES_DIR) if f.endswith("sonuc.tsv")]
    if not tsv_files:
        st.warning("Henüz sonuç dosyası bulunamadı.")
        st.stop()

    selected = st.selectbox("Bir sonuç dosyası seçiniz:", tsv_files)

    if selected:
        file_path = os.path.join(RETURN_FILES_DIR, selected)
        sample_name = selected.replace(".tsv", "")
        stats_path = os.path.join(STATISTICS_DIR, f"{sample_name}_fraction_coverage.txt")
        st.success(f"**Seçilen Dosya:** {selected}")
        try:
            variant_table_df = pd.read_csv(file_path, sep="\t")
            st.write(f"Toplam Satır Sayısı: {len(variant_table_df)}")

            tabs = st.tabs(["🧬 Varyant Tablosu", "📈 İstatistikler", "📥 Dosya Bilgileri"])
            with tabs[0]:
                st.dataframe(variant_table_df, height=700, width="stretch")
            with tabs[1]:
                if os.path.exists(stats_path):
                    genome_fraction = pd.read_csv(stats_path, sep="\t")
                    st.bar_chart(genome_fraction.set_index("#Coverage (X)"))
                    st.dataframe(genome_fraction, height=500, width="stretch")
                else:
                    st.warning("İstatistik dosyası bulunamadı.")
            with tabs[2]:
                st.write(f"📁 Dosya yolu: `{file_path}`")
                st.download_button(
                    label="💾 Dosyayı İndir",
                    data=open(file_path, "rb").read(),
                    file_name=selected,
                    mime="text/tab-separated-values"
                )
        except Exception as e:
            st.error(f"Dosya yüklenirken bir hata oluştu: {e}")
        

# ==============================
# ✅ NEW RUN PAGE
# ==============================
elif page == "Yeni Çalışma":
    st.title("⚙️ Yeni Çalışma Oluştur")
    st.markdown("""
    <div style='background-color:#ecf2f7; padding:15px; border-radius:8px; border:1px solid #d0d8e0;'>
    <b>💡 Not:</b> Lütfen örnek adını, boşluksuz, ve sonunda <code>_sonuc</code> yazacak şekilde giriniz.
    <br><br>
    Örnek: <code>ornek1_sonuc</code> şeklinde bir isimlendirme yapınız.
    <br><br>
    Bu sayede oluşturulan varyant tablosu dosyası <code>ornek1_sonuc.tsv</code> olarak kaydedilecek ve
    sonuçlar sayfasında otomatik olarak listelenecektir. <code>_sonuc</code> eki eklenmediği takdirde otomatik eklenecektir.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔧 Pipeline Ayarları")
    sample = st.text_input("Örnek Adı")
    
    # --- VCF Yükleme Seçeneği ---
    st.markdown("#### 📃 VCF Dosya Seçimi")

    upload_option = st.radio(
        "Dosya kaynağını seçin:",
        ["💻 Kendi Bilgisayarımdan Yükle", "📁 Sunucudaki Bir Klasörden Seç"],
        horizontal=True
    )

    vcf_path = None

    if upload_option == "💻 Kendi Bilgisayarımdan Yükle":
        uploaded_vcf = st.file_uploader("VCF Dosyasını Yükleyin", type=["vcf"])
        if uploaded_vcf is not None:
            upload_dir = "input_files"
            os.makedirs(upload_dir, exist_ok=True)
            vcf_path = os.path.join(upload_dir, uploaded_vcf.name)
            with open(vcf_path, "wb") as f:
                f.write(uploaded_vcf.getbuffer())
            st.success(f"✅ Dosya yüklendi: {uploaded_vcf.name}")

    elif upload_option == "📁 Sunucudaki Bir Klasörden Seç":
        MEDIA_ROOT = "/media/enes"
        if not os.path.exists(MEDIA_ROOT):
            st.error(f"{MEDIA_ROOT} dizini bulunamadı.")
            st.stop()

        disks = [d for d in os.listdir(MEDIA_ROOT) if os.path.isdir(os.path.join(MEDIA_ROOT, d))]
        if not disks:
            st.warning("💾 Takılı harici disk bulunamadı.")
            st.stop()

        selected_disk = st.selectbox("💾 Bir disk seçiniz:", disks)
        base_dir = os.path.join(MEDIA_ROOT, selected_disk)

        # Geçerli dizini session'da tut
        if "current_dir" not in st.session_state:
            st.session_state["current_dir"] = base_dir

        current_dir = st.session_state["current_dir"]
        st.markdown(f"📂 **Şu anki dizin:** `{current_dir}`")

        # Geri dönme butonu
        if current_dir != base_dir:
            if st.button("⬅️ Üst klasöre dön"):
                st.session_state["current_dir"] = os.path.dirname(current_dir)
                st.rerun()

        entries = os.listdir(current_dir)
        subdirs = [f for f in entries if os.path.isdir(os.path.join(current_dir, f))]
        vcf_files = [f for f in entries if f.endswith((".vcf", ".vcf.gz"))]

        # Alt klasörleri butonlarla göster
        if subdirs:
            st.markdown("### 📂 Alt Klasörler")
            cols = st.columns(3)
            for i, folder in enumerate(subdirs):
                if cols[i % 3].button(f"📁 {folder}"):
                    st.session_state["current_dir"] = os.path.join(current_dir, folder)
                    st.rerun()
        else:
            st.info("Bu dizinde alt klasör yok.")

        # VCF dosyaları
        if vcf_files:
            st.markdown("### 📄 Bulunan VCF Dosyaları")
            selected_file = st.radio("Bir dosya seç:", vcf_files, horizontal=False)
            if selected_file:
                vcf_path = os.path.join(current_dir, selected_file)
                st.success(f"✅ Seçilen dosya: {vcf_path}")
        else:
            st.warning("Bu dizinde `.vcf` dosyası bulunamadı.")

    kit = st.text_input("Kit (örnek: nexome_plus_panel_target)")
    genes = st.text_input("Genler (virgülle ayrılmış)", value="")
    hpo_terms = st.text_input("HPO Terimleri", value="-")

    if st.button("⚙️ Run konfigürasyonunu oluştur"):
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
        df["sample"] = df["sample"].apply(lambda x: x if x.endswith("_sonuc") else f"{x}_sonuc")
        df.to_csv("single_sample/samples_vcf.csv", sep="\t", index=False)
        st.success("✅ samples_vcf.csv başarıyla oluşturuldu.")
        st.dataframe(df, width="stretch", hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Pipeline'ı Çalıştır"):
            run_docker_pipeline()
    with col2:
        if "pipeline_process" in st.session_state and st.session_state["pipeline_process"].poll() is None:
            if st.button("⛔ Pipeline'ı Durdur"):
                stop_pipeline()
