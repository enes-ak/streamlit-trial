import streamlit as st
import pandas as pd
import plotly.express as px

RUN_HISTORY = "single_sample/run_history.csv"

def profile_page():
    st.title("👤 Profil")

    # CSV oku
    df = pd.read_csv(RUN_HISTORY)

    # timestamp’i datetime’a çevir
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # ---- ANALİZ SAYILARI ----
    total_runs = len(df)
    kit_counts = df['kit'].value_counts()

    # DataFrame formatına çevir
    kit_df = kit_counts.reset_index()
    kit_df.columns = ["Kit", "Kullanım Sayısı"]

    most_used_kit = kit_counts.idxmax()
    last_run_time = df['timestamp'].max()
    last_run_kit = df.sort_values('timestamp').iloc[-1]['kit']

    st.subheader("📊 Analiz İstatistikleri")

    st.metric("Toplam Analiz Sayısı", total_runs)

    # ---- KIT DAĞILIMI ----
    st.write("### 🔬 Kit Dağılımı")

    fig = px.pie(
        kit_df,
        names="Kit",
        values="Kullanım Sayısı",
        hole=0.45,  # daha modern donut görünümü
    )

    # Daha şık görünüm
    fig.update_layout(
        height=340,
        margin=dict(l=30, r=30, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_traces(
        textinfo="percent",
        textfont_size=14
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- ÖZET BİLGİLER ----
    st.write("### 🧬 Özet Bilgiler")
    st.write(f"- **En Çok Kullanılan Kit:** {most_used_kit}")
    st.write(f"- **Son Analiz Zamanı:** {last_run_time}")
    st.write(f"- **Son Kullanılan Kit:** {last_run_kit}")

    # ---- TABLO ----
    st.write("### 📦 Kit Kullanım Tablosu")
    st.dataframe(kit_df, hide_index=True)
