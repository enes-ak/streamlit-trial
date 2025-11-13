# import streamlit as st
# import subprocess
# import yaml
# import os
# import signal

# CONFIG = yaml.safe_load(open("config/app_config.yaml"))

# def run_pipeline():
#     image = CONFIG["docker"]["image"]
#     mounts = CONFIG["docker"]["mounts"]
#     snakemake_cmd = CONFIG["snakemake"]["cmd"]

#     docker_cmd = ["docker", "run", "--rm"]

#     for m in mounts:
#         docker_cmd += ["-v", f"{m['host']}:{m['container']}"]

#     docker_cmd += ["--entrypoint", "bash", image, "-c", snakemake_cmd]

#     st.markdown("### Pipeline Çalışıyor...")

#     process = subprocess.Popen(
#         docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#         text=True, bufsize=1
#     )
#     st.session_state["pipeline_process"] = process

#     log_box = st.empty()

#     log_container_style = """
#     <div style="
#         background-color: #f1f5f9;
#         color: #1e293b;
#         font-family: monospace;
#         padding: 12px;
#         border-radius: 8px;
#         height: 600px;
#         overflow-y: auto;
#         white-space: pre-wrap;
#         line-height: 1.4;
#         font-size: 13px;
#         border: 1px solid #cbd5e1;
#         width: 100%;
#         margin: auto;
#     ">
#     {content}
#     </div>
#     """

#     log_text = ""

#     for line in process.stdout:
#         log_text += line
#         safe_text = log_text.replace("<", "&lt;").replace(">", "&gt;")
#         log_box.markdown(log_container_style.format(content=safe_text), unsafe_allow_html=True)

#     process.wait()

#     if process.returncode == 0:
#         st.success("Pipeline başarıyla tamamlandı.")
#     else:
#         st.error("Pipeline hata ile sonlandı.")

# def stop_pipeline():
#     if "pipeline_process" in st.session_state:
#         proc = st.session_state["pipeline_process"]
#         if proc and proc.poll() is None:
#             os.kill(proc.pid, signal.SIGTERM)
#             st.warning("Pipeline durduruldu.")

import streamlit as st
import subprocess
import yaml
import os
import signal

CONFIG = yaml.safe_load(open("config/app_config.yaml"))

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
