import streamlit as st
import os

def input_vcf_selector():
    st.markdown("### 🔽 VCF Dosyası Seç")

    option = st.radio(
        "Dosya kaynağını seçin:",
        ["💻 Bilgisayarımdan Yükle", "📁 Sunucudaki Bir Klasörden Seç"],
        horizontal=True
    )

    vcf_path = None

    # ----------------------
    # Bilgisayardan Yükleme
    # ----------------------
    if option == "💻 Bilgisayarımdan Yükle":
        uploaded = st.file_uploader("VCF Yükle", type=["vcf", "vcf.gz"])
        if uploaded:
            os.makedirs("input_files", exist_ok=True)
            vcf_path = os.path.join("input_files", uploaded.name)
            with open(vcf_path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.success(f"Yüklendi: {uploaded.name}")

    # ----------------------
    # Sunucudan Seç
    # ----------------------
    else:
        MEDIA_ROOT = "/media/enes"

        if not os.path.exists(MEDIA_ROOT):
            st.error(f"{MEDIA_ROOT} bulunamadı!")
            return None

        disks = [d for d in os.listdir(MEDIA_ROOT) if os.path.isdir(os.path.join(MEDIA_ROOT, d))]

        selected_disk = st.selectbox("💾 Disk Seç", disks)
        base_dir = os.path.join(MEDIA_ROOT, selected_disk)

        if "current_dir" not in st.session_state:
            st.session_state["current_dir"] = base_dir

        current_dir = st.session_state["current_dir"]

        st.markdown(f"📂 **Dizin:** `{current_dir}`")

        # Üste çık
        if current_dir != base_dir:
            if st.button("⬅️ Üst Klasöre Dön"):
                st.session_state["current_dir"] = os.path.dirname(current_dir)
                st.rerun()

        entries = os.listdir(current_dir)
        subdirs = [f for f in entries if os.path.isdir(os.path.join(current_dir, f))]
        files = [f for f in entries if f.endswith((".vcf", ".vcf.gz"))]

        # Alt klasörler
        if subdirs:
            st.markdown("### 📁 Alt Klasörler")
            cols = st.columns(3)
            for i, folder in enumerate(subdirs):
                if cols[i % 3].button(folder):
                    st.session_state["current_dir"] = os.path.join(current_dir, folder)
                    st.rerun()

        # VCF Dosyaları
        if files:
            st.markdown("### 📄 VCF Dosyaları")
            selected_file = st.radio("Dosya seç:", files)
            if selected_file:
                vcf_path = os.path.join(current_dir, selected_file)
                st.success(f"Seçilen: {vcf_path}")

    return vcf_path
