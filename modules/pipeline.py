import os
import streamlit as st
import subprocess
import yaml
import signal
import pandas as pd
from datetime import datetime


CONFIG = yaml.safe_load(open("config/app_config.yaml"))

def to_container_path(path: str) -> str:
    """
    Host path'ini docker container içindeki karşılığına çevirir.
    - Sunucudan seçilen tam path'ler için: /media/... → /host/media/...
    - Zaten container path'i verilmişse (örn /pipeline/input_files/...), olduğu gibi bırakır.
    """
    # Eğer zaten container içinde beklenen prefixlerden biriyse, dokunma
    if path.startswith("/pipeline/") or path.startswith("/host/"):
        return path

    # Sunucu path'i (absolute) ise /host ile map et
    if os.path.isabs(path):
        return f"/host{path}"

    # Göreli path'leri (input_files içinden vs.) istersen burada ele alabilirsin
    return path


def log_run(sample_name, kit, hpo_term, genes, base_dir="data", overwrite=False):
    history_path = os.path.join(base_dir, "run_history.csv")

    # Eğer history varsa önce oku
    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)

        # Sample zaten varsa
        if sample_name in df_hist["sample_name"].values:
            if not overwrite:
                # Overwrite izni yok → kullanıcıya UI içinde sorulacak
                return "exists"
            else:
                # Overwrite true → eski kaydı sil
                df_hist = df_hist[df_hist["sample_name"] != sample_name]
                df_hist.to_csv(history_path, index=False)

    # Yeni kaydı ekle
    record = {
        "timestamp": datetime.now().strftime("%d/%m/%Y - %H:%M"),
        "sample_name": sample_name,
        "kit": kit,
        "hpo_term": hpo_term,
        "genes": genes
    }

    df_new = pd.DataFrame([record])

    header = not os.path.exists(history_path)
    df_new.to_csv(history_path, mode="a", header=header, index=False)

    return "added"

def run_pipeline():
    image = CONFIG["docker"]["image"]
    mounts = CONFIG["docker"]["mounts"]
    snakemake_cmd = CONFIG["snakemake"]["cmd"]

    docker_cmd = ["docker", "run", "--rm"]

    for m in mounts:
        docker_cmd += ["-v", f"{m['host']}:{m['container']}"]

    docker_cmd += ["--entrypoint", "bash", image, "-c", snakemake_cmd]

    # pipeline status
    st.session_state["pipeline_status"] = "running"

    # launch process (non-blocking)
    process = subprocess.Popen(
        docker_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0,
        universal_newlines=True
    )

    # save process object
    st.session_state["pipeline_process"] = process
    st.session_state["progress"] = 0
    st.session_state["pipeline_log"] = ""


def stop_pipeline():
    """Pipeline çalışan prosesi öldürür."""
    if "pipeline_process" in st.session_state:
        process = st.session_state["pipeline_process"]
        if process and process.poll() is None:
            os.kill(process.pid, signal.SIGTERM)
            st.session_state["pipeline_status"] = "stopped"
            st.warning("Pipeline durduruldu.")
