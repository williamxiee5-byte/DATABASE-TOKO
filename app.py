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
        box-shadow: 0 8px 24px -4px rgba(234, 88, 12, 0.06) !important;
    }

    [data-testid="stMetric"] {
        background-color: rgba(255, 247, 237, 0.92) !important;
        border: 1px solid rgba(253, 186, 116, 0.5) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        box-shadow: 0 2px 6px rgba(234, 88, 12, 0.04) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        color: #9a3412 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #431407 !important;
    }

    .card-product-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #9a3412;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .card-product-sub {
        font-size: 0.95rem;
        color: #c2410c;
        font-weight: 600;
        margin-bottom: 14px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid rgba(251, 146, 60, 0.3);
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 700;
        background-color: rgba(255, 237, 213, 0.6);
        color: #9a3412;
        border: 1px solid rgba(253, 186, 116, 0.35);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ea580c, #c2410c) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.28) !important;
    }

    .stButton>button[kind="primary"] {
        border-radius: 10px;
        font-weight: 700;
        background: linear-gradient(135deg, #f97316, #ea580c) !important;
        border: none !important;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.28) !important;
        color: #ffffff !important;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(234, 88, 12, 0.38) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 3. SISTEM AUTHENTICATION & LOGIN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

if not st.session_state["logged_in"]:
    st.markdown(
        """<div class="main-title" style="text-align: center; margin-top: 40px;">🛒 Toko Management Dashboard</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="main-subtitle" style="text-align: center;">Sistem Terproteksi. Silakan login atau ajukan akses ke Master Admin.</div>""",
        unsafe_allow_html=True,
    )

    col_l, col_form, col_r = st.columns([1, 1.2, 1])

    with col_form:
        with st.container(border=True):
            tab_login, tab_reg = st.tabs(
                ["🔐 Masuk (Login)", "📝 Minta Akses (Daftar)"]
            )

            with tab_login:
                st.markdown("##### Masuk ke Dashboard")
                log_user = st.text_input("Username / Akses ID", key="login_user")
                log_pass = st.text_input("Password", type="password", key="login_pass")

                if st.button(
                    "Masuk ke Sistem",
                    type="primary",
                    use_container_width=True,
                ):
                    if not log_user.strip() or not log_pass.strip():
                        st.warning("⚠️ Masukkan Username dan Password!")
                    else:
                        try:
                            res_u = (
                                supabase.table("users_akses")
                                .select("*")
                                .eq("username", log_user.strip())
                                .execute()
                            )
                            if not res_u.data:
                                st.error("❌ Username tidak terdaftar!")
                            else:
                                user_data = res_u.data[0]
                                if user_data["password"] != log_pass:
                                    st.error("❌ Password salah!")
                                elif user_data.get("status_akses") != "approved":
                                    st.warning("⚠️ Akun Anda belum disetujui oleh Master Admin!")
                                else:
                                    # Berhasil Login
                                    st.session_state["logged_in"] = True
                                    st.session_state["user_role"] = user_data.get("role")
                                    st.session_state["username"] = user_data["username"]
                                    st.session_state["user_name"] = user_data.get("nama_lengkap", user_data["username"])
                                    st.rerun() # Refresh halaman agar masuk ke dashboard utama
                        except Exception as e:
                            st.error(f"❌ Terjadi kesalahan saat memverifikasi data: {e}")
            
            with tab_reg:
                st.info("Form permintaan akses dapat diisi di sini (TBA).")

# ==========================================
# 4. DASHBOARD UTAMA (JIKA SUDAH LOGIN)
# ==========================================
else:
    col_kiri, col_kanan = st.columns([4, 1])
    with col_kiri:
        st.markdown(f"### 👋 Selamat Datang, {st.session_state['user_name']}!")
    with col_kanan:
        if st.button("Keluar (Logout)", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    st.write("---")
    st.success("Anda berhasil login. Silakan masukkan konten dashboard