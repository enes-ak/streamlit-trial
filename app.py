import streamlit as st
import pandas as pd

# Sayfa ayarları: tam genişlik
st.set_page_config(
    page_title="Massive Analyser",
    layout="wide"
)

# Üst başlık
st.markdown("## Massive Analyser RIP ⚰️")

# Tek sekme oluştur
tabs = st.tabs(["Varyant Tablosu", "İstatistik"])

with tabs[0]:
    st.subheader("Varyant Tablosu")
    
    # DataFrame yükleme
    df = pd.read_csv(
        "/home/enes/Desktop/pipelines/single_sample/data_bayram_hoca/return_files/barcode07.tsv",
        sep="\t"
    )
    
    # Tabloyu tam genişlik ve yüksek göster
    st.dataframe(df, width="stretch", height=600)



with tabs[1]:
    st.subheader("İstatistik")
    st.write("Genomic Fraction Bar-Chart")
    genome_fraction = pd.read_csv("/home/enes/Desktop/pipelines/single_sample/data_bayram_hoca/statistics_bam/qualimap/barcode06/raw_data_qualimapReport/genome_fraction_coverage.txt", sep="\t")
    st.bar_chart(genome_fraction.set_index("#Coverage (X)")) 
    st.write("Genomic Fraction Raw Data")
    st.dataframe(genome_fraction,width="stretch", height=600)