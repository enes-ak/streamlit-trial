import streamlit as st

def load_styles():
    st.markdown("""
    <style>
        body { background-color: #f7f9fb; }
        h1, h2, h3, h4 { color:#1f4e79 !important; }

        .stButton>button {
            background-color:#1f77b4;
            color:white;
            border-radius:6px;
            font-weight:500;
        }
        .stButton>button:hover {
            background-color:#145a8a;
        }

        section[data-testid="stSidebar"] {
            background-color:#ecf2f7;
        }
    </style>
    """, unsafe_allow_html=True)
