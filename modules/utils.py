import streamlit as st
import pandas as pd
import math
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


# --------------------------------
#  1) ADVANCED (GLOBAL) FILTER UI
# --------------------------------
def advanced_filter_panel(df, filter_columns, reset=False):
    st.subheader("🔍 İleri Düzey Filtre")

    filtered_df = df.copy()

    for col in filter_columns:
        col_data = df[col]

        with st.expander(f"🧩 {col}", expanded=False):

            # -----------------------------
            # STRING FILTER
            # -----------------------------
            if col_data.dtype == object:
                if reset:
                    default = ""
                else:
                    default = st.session_state.get(f"adv_txt_{col}", "")

                val = st.text_input(
                    f"{col} içerir:",
                    value=default,
                    key=f"adv_txt_{col}"
                )

                if val:
                    mask = filtered_df[col].astype(str).str.contains(val, case=False, na=False)
                    filtered_df = filtered_df[mask]


            # -----------------------------
            # NUMERIC FILTER
            # -----------------------------
            elif pd.api.types.is_numeric_dtype(col_data):

                true_min = float(df[col].min())
                true_max = float(df[col].max())

                # Eğer tüm değerler aynıysa slider YASAK → info göster
                if true_min == true_max:
                    st.info(f"{col} için filtre uygulanamaz (tüm değerler = {true_min})")
                    continue

                # Reset mode → full range
                if reset:
                    default_range = (true_min, true_max)
                else:
                    default_range = st.session_state.get(
                        f"adv_rng_{col}", (true_min, true_max)
                    )

                a, b = st.slider(
                    f"{col} aralığı",
                    min_value=true_min,
                    max_value=true_max,
                    value=default_range,
                    key=f"adv_rng_{col}"
                )

                mask = (filtered_df[col].between(a, b)) | (filtered_df[col].isna())
                filtered_df = filtered_df[mask]


            # -----------------------------
            # CATEGORY FILTER
            # -----------------------------
            elif df[col].nunique() <= 30:
                options = sorted(df[col].dropna().unique().tolist())

                if reset:
                    default_vals = []
                else:
                    default_vals = st.session_state.get(f"adv_cat_{col}", [])

                selected = st.multiselect(
                    f"{col} seç",
                    options,
                    default=default_vals,
                    key=f"adv_cat_{col}"
                )

                if selected:
                    mask = filtered_df[col].isin(selected) | filtered_df[col].isna()
                else:
                    mask = pd.Series([True] * len(filtered_df))

                filtered_df = filtered_df[mask]

    return filtered_df





# --------------------------------
#  2) FINAL: ADVANCED + SLICE + AGGRID
# --------------------------------
def advanced_filtered_paginated_aggrid(df, filter_columns, page_size=1000):
    # --- BUTTON AREA ---
    show_advanced = st.toggle("🔧 İleri Düzey Filtreyi Aç/Kapat")

    reset = st.button("🔄 Tüm Filtreleri Sıfırla")

    if reset:
        for k in list(st.session_state.keys()):
            if k.startswith("adv_"):
                del st.session_state[k]
        st.session_state["adv_reset"] = True
        st.rerun()
    else:
        st.session_state["adv_reset"] = False
    
    # --- APPLY ADVANCED FILTERS ---
    if show_advanced:
        df_filtered = advanced_filter_panel(df, filter_columns)
    else:
        df_filtered = df

    # --- PAGINATION ---
    total_rows = len(df_filtered)
    total_pages = max(1, math.ceil(total_rows / page_size))

    page = st.number_input("Sayfa", min_value=1, max_value=total_pages, value=1)
    start = (page - 1) * page_size
    end = start + page_size

    sliced = df_filtered.iloc[start:end]

    st.write(f"Toplam eşleşen satır: {total_rows:,}")
    st.write(f"Gösterilen: {start+1:,} → {min(end, total_rows):,}")

    # --- AGGRID TABLE (LOCAL FILTERING) ---
    gb = GridOptionsBuilder.from_dataframe(sliced)
    gb.configure_default_column(
        filter=True, sortable=True, resizable=True,
        wrapText=False, autoHeight=False, minWidth=150
    )
    grid_options = gb.build()

    AgGrid(
        sliced,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.FILTERING_CHANGED,
        allow_unsafe_jscode=True,
        height=650
    )
