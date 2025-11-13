import streamlit as st
import pandas as pd
from modules.input_select import input_vcf_selector
from modules.pipeline import run_pipeline, stop_pipeline
from streamlit_autorefresh import st_autorefresh


def new_run_page():
    st.title("⚙️ Yeni Çalışma Oluştur")

    sample = st.text_input("Örnek adı")
    vcf_path = input_vcf_selector()
    kit = st.text_input("Kit")
    genes = st.text_input("Genler (virgülle ayrılmış) / Yoksa '-' ", value="-")
    hpo_terms = st.text_input("HPO Terimleri (virgülle ayrılmış) / Yoksa '-' ", value="-")

    st.markdown("---")

    # -----------------------------
    # KONFİG OLUŞTUR
    # -----------------------------
    if st.button("⚙️ Çalışma konfigürasyonu oluştur"):
        if not sample:
            st.error("❗ Örnek adı boş bırakılamaz.")
            st.stop()
        
        if not kit:
            st.error("❗ Kit alanı boş bırakılamaz.")
            st.stop()
        df = pd.DataFrame([{
            "sample": sample if sample.endswith("_sonuc") else f"{sample}_sonuc",
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

        st.session_state["last_config_df"] = df
        st.session_state["config_ready"] = True
        st.success("Konfigürasyon oluşturuldu.")

    # Konfigürasyonu göster
    if "last_config_df" in st.session_state:
        st.markdown("### ⚙️ Çalışma Konfigürasyonu")
        COLS_TO_SHOW = ["sample","vcf_path","kit","genes","hpo_terms"]
        st.dataframe(st.session_state["last_config_df"][COLS_TO_SHOW], width="stretch", hide_index=True)

    st.markdown("---")

    # Pipeline durumu
    running = (
        "pipeline_process" in st.session_state and
        st.session_state["pipeline_process"] is not None and
        st.session_state["pipeline_process"].poll() is None
    )

    col1, col2 = st.columns(2)

    # BAŞLAT
    with col1:
        if not running and st.session_state.get("config_ready"):
            if st.button("▶️ Pipeline'ı Çalıştır"):
                run_pipeline()

    # DURDUR
    with col2:
        if running:
            if st.button("⛔ Pipeline'ı Durdur"):
                stop_pipeline()

    # -----------------------------
    # LOG STREAMING GERÇEK LOOP
    # -----------------------------
    if running:

        # Sayfayı 0.8 saniyede bir yeniden çalıştır
        st_autorefresh(interval=800, key="pipeline_refresh")

        st.markdown("### 🚀 Pipeline Çalışıyor...")

        # Progress bar
        progress_bar = st.progress(st.session_state.get("progress", 0))
        status_text = st.empty()

        proc = st.session_state["pipeline_process"]

        # Bir satır log oku
        line = proc.stdout.readline()

        if line:
            st.session_state["status_line"] = line

            # Satırdan yüzde çıkar
            # Örn: "25 of 55 steps (45%) done"
            if "steps" in line and "%" in line:
                try:
                    percent = int(line.split("(")[1].split("%")[0])
                    st.session_state["progress"] = percent / 100
                except:
                    pass

        # UI Güncelle
        progress_bar.progress(st.session_state["progress"])
        status_text.write(f'Pipeline ilerleme yüzdesi: %{round(st.session_state["progress"]*100,3)}')
    # -----------------------------
    # PIPELINE BİTTİYSE
    # -----------------------------
    elif "pipeline_process" in st.session_state:
        ret = st.session_state["pipeline_process"].poll()
        if ret == 0:
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
        elif ret is not None:
            st.error("❌ Pipeline hata ile sonlandı. Logları kontrol edin.")
