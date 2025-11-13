import streamlit as st
import pandas as pd
import os

RETURN_FILES_DIR = "single_sample/data/return_files"
STAT_DIR = "data/statistics"

def results_page():
    st.title("📊 Analiz Sonuçları")

    if not os.path.exists(RETURN_FILES_DIR):
        st.warning("Sonuç klasörü bulunamadı.")
        return

    tsv_files = [f for f in os.listdir(RETURN_FILES_DIR) if f.endswith("sonuc.tsv")]

    if not tsv_files:
        st.info("Henüz sonuç yok.")
        return

    selected = st.selectbox("Dosya seç:", tsv_files)
    file_path = os.path.join(RETURN_FILES_DIR, selected)

    df = pd.read_csv(file_path, sep="\t")

    st.write(f"Toplam satır: {len(df)}")
    tabs = st.tabs(["🧬 Varyant Tablosu", "📈 İstatistikler"])

    with tabs[0]:
        st.dataframe(df, height=600, width="stretch")
        right_col = st.columns([0.85, 0.15])[1]
        with right_col:
            st.download_button(
                label="📥 İndir",
                data=open(file_path, "rb").read(),
                file_name=selected,
                mime="text/tab-separated-values",
                width="stretch"
            )
    

    with tabs[1]:
        sample = selected.replace(".tsv", "")
        stat_path = os.path.join(STAT_DIR, f"{sample}_fraction_coverage.txt")

        if os.path.exists(stat_path):
            stat_df = pd.read_csv(stat_path, sep="\t")
            st.bar_chart(stat_df.set_index("#Coverage (X)"))
            st.dataframe(stat_df, height=500)
        else:
            st.warning("İstatistik bulunamadı.")