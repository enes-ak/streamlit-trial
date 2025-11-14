import os
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


RETURN_FILES_DIR = "single_sample/data/return_files"
STAT_DIR = "data/statistics"
RUN_HISTORY = "single_sample/run_history.csv"

def show_variant_table(df):

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        minWidth=150,  
        filter=True,
        sortable=True,
        resizable=True,
        wrapText=False,       # doğru
        autoHeight=False
    )

    # string kolonlar
    for col in df.select_dtypes(include=["object"]).columns:
        gb.configure_column(col, filter="agTextColumnFilter")

    # numerik kolonlar
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        gb.configure_column(col, filter="agNumberColumnFilter")

    # kategori kolonı
    if "Main.gene_symbol" in df.columns:
        gb.configure_column("Main.gene_symbol", filter="agSetColumnFilter")

    # 🔥 kolonları tablo yüklenince otomatik genişlet
    gb.configure_grid_options(
        onFirstDataRendered="function(params) { params.api.autoSizeAllColumns(); }"
    )

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.FILTERING_CHANGED,
        allow_unsafe_jscode=True,
        height=650,
        fit_columns_on_grid_load=False
    )

    return grid_response



def results_page():
    st.title("📊 Analiz Sonuçları")

    # run_history yoksa çık
    if not os.path.exists(RUN_HISTORY):
        st.warning("run_history.csv bulunamadı.")
        return

    # CSV'yi yükle
    history = pd.read_csv(RUN_HISTORY)

    if history.empty:
        st.info("Henüz kayıtlı bir çalışma yok.")
        return

    st.subheader("📁 Mevcut Çalışmalar")

    # Kullanıcıya gösterilecek tablo
    show_cols = ["timestamp", "sample_name", "kit", "genes", "hpo_term"]
    # show_cols = ["Tarih", "Örnek Adı", "Kit", "Genler", "HPO Terimleri"]
    history.columns = show_cols
    selected = st.dataframe(
        history[show_cols],
        selection_mode="single-row",
        on_select="rerun",
        width="stretch",
        height=400,
        key="history_table"
    )

    # Kullanıcı bir satıra tıklamazsa hiçbir şey yapma
    if not selected or not selected["selection"]["rows"]:
        st.info("Lütfen bir run seçin.")
        return

    # Seçilen satır
    idx = selected["selection"]["rows"][0]
    chosen = history.iloc[idx]
    st.success(f"🔍 Seçilen çalışma: **{chosen['sample_name']}**")

    # Sonuç dosyasının path'i
    sample_name = chosen["sample_name"]
    result_file = f"{sample_name}.tsv"
    result_path = os.path.join(RETURN_FILES_DIR, result_file)

    # Dosya gerçekten var mı?
    if not os.path.exists(result_path):
        st.error(f"Sonuç dosyası bulunamadı: {result_file}")
        return

    # Sonuçları yükle
    df = pd.read_csv(result_path, sep="\t")

    tabs = st.tabs(["🧬 Varyant Tablosu", "📈 İstatistikler"])

    # ---------------------------
    #  VARYANT TABLOSU
    # ---------------------------
    with tabs[0]:
        st.write(f"Toplam satır: {len(df)}")
        show_variant_table(df)

        st.download_button(
            label="📥 Sonuçları İndir",
            data=open(result_path, "rb").read(),
            file_name=result_file,
            mime="text/tab-separated-values"
        )

    # ---------------------------
    #  İSTATİSTİKLER
    # ---------------------------
    with tabs[1]:
        stat_path = os.path.join(STAT_DIR, f"{sample_name}_fraction_coverage.txt")

        if os.path.exists(stat_path):
            stat_df = pd.read_csv(stat_path, sep="\t")
            st.bar_chart(stat_df.set_index("#Coverage (X)"))
            st.dataframe(stat_df, width="stretch", height=500)
        else:
            st.warning("İstatistik bulunamadı.")
