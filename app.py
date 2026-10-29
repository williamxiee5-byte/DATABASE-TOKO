from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==========================================
# 1. KONFIGURASI SUPABASE CLOUD
# ==========================================
SUPABASE_URL = "https://iarlfrjsyihvgrptvrdy.supabase.co"
SUPABASE_KEY = "sb_publishable_T8ItYv0nRWIo2PZRXfBFBA_nPtCudAQ"
BUCKET_NAME = "produk-foto"


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"Gagal terhubung ke Supabase: {e}")
    st.stop()

# ==========================================
# 2. KONFIGURASI TEMA & STYLING
# ==========================================
st.set_page_config(
    page_title="GM Dashboard - HPP & Margin",
    page_icon="🛒",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #fffaf5 !important;
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(255, 237, 213, 0.7) 0%, transparent 45%),
            radial-gradient(circle at 85% 80%, rgba(254, 215, 170, 0.5) 0%, transparent 45%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ea580c' stroke-width='1.1' stroke-linecap='round' stroke-linejoin='round' opacity='0.05'%3E%3Ccircle cx='8' cy='21' r='1'/%3E%3Ccircle cx='19' cy='21' r='1'/%3E%3Cpath d='M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12'/%3E%3C/svg%3E") !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-size: 580px 580px !important;
        background-attachment: fixed !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(255, 250, 245, 0.5) !important;
        backdrop-filter: blur(8px) !important;
    }

    .main-title {
        font-weight: 800;
        font-size: 2.1rem;
        color: #9a3412;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        color: #c2410c;
        opacity: 0.85;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(251, 146, 60, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 24px -4px rgba(234, 88
