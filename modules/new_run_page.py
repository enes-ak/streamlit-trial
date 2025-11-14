import streamlit as st
import pandas as pd
from modules.input_select import input_vcf_selector
from modules.pipeline import run_pipeline, stop_pipeline, log_run, to_container_path
from streamlit_autorefresh import st_autorefresh


def new_run_page():
    st.title("⚙️ Yeni Çalışma Oluştur")
    st.markdown("""
    <div style='background-color:#ecf2f7; padding:15px; border-radius:8px; border:1px solid #d0d8e0;'>
    <b>💡 Not:</b> Lütfen örnek adını, boşluksuz, ve sonunda <code>_sonuc</code> yazacak şekilde giriniz.
    <br>
    Bu sayede oluşturulan varyant tablosu dosyası <code>ornek1_sonuc.tsv</code> olarak kaydedilecek ve
    sonuçlar sayfasında otomatik olarak listelenecektir. <code>_sonuc</code> eki eklenmediği takdirde otomatik eklenecektir.
    <br><br>
    <b>Örnek:</b> <code>ornek1_sonuc</code> şeklinde bir isimlendirme yapınız.
    <br><br>

    </div>
    """, unsafe_allow_html=True)
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


        container_vcf_path = to_container_path(vcf_path)

        df = pd.DataFrame([{
            "sample": sample if sample.endswith("_sonuc") else f"{sample}_sonuc",
            "vcf_path": container_vcf_path,     # 🔥 artık her zaman doğru path
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
        row = df.iloc[0]

        # İlk log_run denemesi, overwrite kapalı
        res = log_run(
            sample_name = row["sample"],
            kit = row["kit"],
            hpo_term = row["hpo_terms"],
            genes = row["genes"],
            base_dir = "single_sample"
        )

        if res == "exists":
            st.warning(f"⚠️ '{row['sample']}' isimli örnek zaten mevcut. "
                    "Lütfen örnek ismini değiştirin ya da üzerine yazın.")

            if st.button("🔁 Üzerine yaz"):
                log_run(
                    sample_name=row["sample"],
                    kit=row["kit"],
                    hpo_term=row["hpo_terms"],
                    genes=row["genes"],
                    base_dir="single_sample",
                    overwrite=True
                )
                st.success("✔ Eski çalışma silindi, yenisi kaydedildi.")
                st.stop()

            st.stop()

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

    col1, col2 = st.columns([0.38, 0.62])

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
