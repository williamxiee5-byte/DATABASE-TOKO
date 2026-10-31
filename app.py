from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==========================================
# 1. KONFIGURASI SUPABASE CLOUD & UTILS
# ==========================================
SUPABASE_URL = "https://iarlfrjsyihvgrptvrdy.supabase.co"
SUPABASE_KEY = "sb_publishable_T8ItYv0nRWIo2PZRXfBFBA_nPtCudAQ"
BUCKET_NAME = "produk-foto"
TABLE_NAME = "produk" # Asumsi nama tabel dari kode lama

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"Gagal terhubung ke Supabase: {e}")
    st.stop()

# Helper Functions
def as_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def rupiah(val):
    return f"Rp {int(val):,}".replace(",", ".")

def calculate(draft: dict) -> dict:
    hpp_total = (
        draft.get("hpp_barang", 0) + 
        draft.get("biaya_kemasan", 0) + 
        draft.get("biaya_tenaga_kerja", 0) + 
        draft.get("biaya_lain", 0)
    )
    harga_jual = draft.get("harga_jual", 0)
    fee_rp = harga_jual * (draft.get("fee_marketplace_pct", 0) / 100.0)
    affiliate_rp = harga_jual * (draft.get("affiliate_pct", 0) / 100.0)
    ads_unit = draft.get("biaya_iklan_per_unit", 0)
    
    # Menambahkan biaya transaksi Rp 1.250 per pesanan
    biaya_transaksi = 1250 
    
    total_cost = hpp_total + fee_rp + affiliate_rp + ads_unit + biaya_transaksi
    profit = harga_jual - total_cost
    margin_pct = (profit / harga_jual * 100) if harga_jual > 0 else 0.0

    return {
        "hpp_total": hpp_total,
        "fee_rp": fee_rp,
        "affiliate_rp": affiliate_rp,
        "biaya_iklan_per_unit": ads_unit,
        "total_biaya": total_cost,
        "laba_bersih": profit,
        "margin_pct": margin_pct,
    }

def fetch_products() -> list:
    response = supabase.table(TABLE_NAME).select("*").order("nama").execute()
    return response.data or []

def upload_photo(uploaded_file, sku_or_name: str) -> str:
    if uploaded_file is None:
        return ""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in sku_or_name)
    safe_name = safe_name.strip("-_") or "produk"
    extension = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else "jpg"
    object_path = f"{safe_name}-{int(datetime.now().timestamp())}.{extension}"
    content_type = uploaded_file.type or "application/octet-stream"
    supabase.storage.from_(BUCKET_NAME).upload(
        path=object_path,
        file=uploaded_file.getvalue(),
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return supabase.storage.from_(BUCKET_NAME).get_public_url(object_path)

def save_product(payload: dict, product_id=None):
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    if product_id:
        supabase.table(TABLE_NAME).update(payload).eq("id", product_id).execute()
    else:
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        supabase.table(TABLE_NAME).insert(payload).execute()


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

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

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

    .main-title { font-weight: 800; font-size: 2.1rem; color: #9a3412; margin-bottom: 0.2rem; letter-spacing: -0.5px; }
    .main-subtitle { color: #c2410c; opacity: 0.85; font-size: 0.95rem; margin-bottom: 1.5rem; font-weight: 500; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important; border: 1px solid rgba(251, 146, 60, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.92) !important; backdrop-filter: blur(12px) !important;
        box-shadow: 0 8px 24px -4px rgba(234, 88, 12, 0.06) !important;
    }

    [data-testid="stMetric"] {
        background-color: rgba(255, 247, 237, 0.92) !important; border: 1px solid rgba(253, 186, 116, 0.5) !important;
        border-radius: 14px !important; padding: 16px !important; box-shadow: 0 2px 6px rgba(234, 88, 12, 0.04) !important;
    }
    [data-testid="stMetricLabel"] { font-size: 0.82rem !important; color: #9a3412 !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
    [data-testid="stMetricValue"] { font-size: 1.7rem !important; font-weight: 800 !important; color: #431407 !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid rgba(251, 146, 60, 0.3); padding-bottom: 8px; }
    .stTabs [data-baseweb="tab"] { height: 44px; border-radius: 10px; padding: 8px 20px; font-weight: 700; background-color: rgba(255, 237, 213, 0.6); color: #9a3412; border: 1px solid rgba(253, 186, 116, 0.35); }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #ea580c, #c2410c) !important; color: #ffffff !important; border: none !important; box-shadow: 0 4px 14px rgba(234, 88, 12, 0.28) !important; }

    .stButton>button[kind="primary"] {
        border-radius: 10px; font-weight: 700; background: linear-gradient(135deg, #f97316, #ea580c) !important; border: none !important;
        padding: 0.6rem 1.2rem; box-shadow: 0 4px 14px rgba(234, 88, 12, 0.28) !important; color: #ffffff !important; transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(234, 88, 12, 0.38) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 3. SISTEM AUTHENTICATION & LOGIN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div class="main-title" style="text-align: center; margin-top: 40px;">🛒 Toko Management Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle" style="text-align: center;">Sistem Terproteksi. Silakan login atau ajukan akses.</div>', unsafe_allow_html=True)

    col_l, col_form, col_r = st.columns([1, 1.2, 1])
    with col_form:
        with st.container(border=True):
            st.markdown("##### Masuk ke Dashboard")
            log_user = st.text_input("Username / Akses ID", key="login_user")
            log_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Masuk ke Sistem", type="primary", use_container_width=True):
                if not log_user.strip() or not log_pass.strip():
                    st.warning("⚠️ Masukkan Username dan Password!")
                else:
                    try:
                        res_u = supabase.table("users_akses").select("*").eq("username", log_user.strip()).execute()
                        if not res_u.data:
                            st.error("❌ Username tidak terdaftar!")
                        else:
                            user_data = res_u.data[0]
                            if user_data["password"] != log_pass:
                                st.error("❌ Password salah!")
                            elif user_data.get("status_akses") != "approved":
                                st.warning("⚠️ Akun Anda belum disetujui oleh Master Admin!")
                            else:
                                st.session_state["logged_in"] = True
                                st.session_state["user_name"] = user_data.get("nama_lengkap", user_data["username"])
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Kesalahan database: {e}")

# ==========================================
# 4. DASHBOARD UTAMA (JIKA SUDAH LOGIN)
# ==========================================
else:
    # Header & Sidebar
    col_kiri, col_kanan = st.columns([4, 1])
    with col_kiri:
        st.markdown(f'<div class="main-title">🛒 GM Dashboard</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="main-subtitle">Selamat datang, {st.session_state["user_name"]}! Kalkulator HPP, laba, dan margin.</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Menu Utama")
        page = st.radio("Navigasi", ["Ringkasan & Daftar Produk", "Tambah Produk", "Edit / Hapus Produk"])
        st.divider()
        st.caption("Data tersimpan di Supabase.")
        if st.button("Keluar (Logout)", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Load Data Produk
    try:
        products = fetch_products()
    except Exception as exc:
        st.error("Tidak bisa membaca tabel Supabase. Pastikan konfigurasi benar.")
        st.stop()

    products_by_id = {str(p.get("id")): p for p in products}

    # Form UI Component
    def product_form(prefix: str, initial: dict | None = None):
        initial = initial or {}
        with st.form(f"{prefix}_form", clear_on_submit=(prefix == "add")):
            st.subheader("Informasi Produk")
            c1, c2, c3 = st.columns(3)
            with c1:
                nama = st.text_input("Nama produk *", value=str(initial.get("nama", "")))
                sku = st.text_input("SKU / kode produk", value=str(initial.get("sku", "")))
            with c2:
                variasi = st.text_input("Variasi", value=str(initial.get("variasi", "")))
                harga_jual = st.number_input("Harga jual (Rp)", min_value=0, step=1000, value=int(as_float(initial.get("harga_jual"))))
            with c3:
                foto = st.file_uploader("Foto produk (opsional)", type=["png", "jpg", "jpeg", "webp"], key=f"{prefix}_photo")
                current_photo = str(initial.get("foto_url", "") or "")
                if current_photo:
                    st.caption("Foto saat ini tersimpan.")

            st.subheader("Komponen HPP per unit")
            a, b, c = st.columns(3)
            with a:
                hpp_barang = st.number_input("Harga beli / bahan (Rp)", min_value=0, step=500, value=int(as_float(initial.get("hpp_barang"))))
                biaya_kemasan = st.number_input("Biaya kemasan (Rp)", min_value=0, step=100, value=int(as_float(initial.get("biaya_kemasan"))))
            with b:
                biaya_tenaga_kerja = st.number_input("Biaya tenaga kerja (Rp)", min_value=0, step=100, value=int(as_float(initial.get("biaya_tenaga_kerja"))))
                biaya_lain = st.number_input("Biaya lain (Rp)", min_value=0, step=100, value=int(as_float(initial.get("biaya_lain"))))
            with c:
                fee_marketplace_pct = st.number_input("Fee marketplace (%)", min_value=0.0, max_value=100.0, step=0.5, value=as_float(initial.get("fee_marketplace_pct", 0)))
                affiliate_pct = st.number_input("Affiliate (%)", min_value=0.0, max_value=100.0, step=0.5, value=as_float(initial.get("affiliate_pct", 0)))
            biaya_iklan_per_unit = st.number_input("Biaya iklan per unit terjual (Rp)", min_value=0, step=100, value=int(as_float(initial.get("biaya_iklan_per_unit"))), help="Isi biaya iklan rata-rata per unit. Jangan isi ROAS di sini.")

            draft = {
                "harga_jual": harga_jual, "hpp_barang": hpp_barang, "biaya_kemasan": biaya_kemasan,
                "biaya_tenaga_kerja": biaya_tenaga_kerja, "biaya_lain": biaya_lain,
                "fee_marketplace_pct": fee_marketplace_pct, "affiliate_pct": affiliate_pct,
                "biaya_iklan_per_unit": biaya_iklan_per_unit,
            }
            result = calculate(draft)
            
            st.divider()
            st.subheader("Simulasi hasil")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total HPP", rupiah(result["hpp_total"]))
            m2.metric("Total biaya (inc. fee & Rp1.250)", rupiah(result["total_biaya"]))
            m3.metric("Laba bersih per unit", rupiah(result["laba_bersih"]))
            m4.metric("Margin bersih", f'{result["margin_pct"]:.2f}%')

            submitted = st.form_submit_button("Simpan Produk" if prefix == "add" else "Simpan Perubahan", type="primary", use_container_width=True)

        if submitted:
            if not nama.strip():
                st.error("Nama produk wajib diisi.")
                return
            payload = {
                "nama": nama.strip(), "sku": sku.strip(), "variasi": variasi.strip(),
                "harga_jual": int(harga_jual), "hpp_barang": int(hpp_barang),
                "biaya_kemasan": int(biaya_kemasan), "biaya_tenaga_kerja": int(biaya_tenaga_kerja),
                "biaya_lain": int(biaya_lain), "fee_marketplace_pct": float(fee_marketplace_pct),
                "affiliate_pct": float(affiliate_pct), "biaya_iklan_per_unit": int(biaya_iklan_per_unit),
                "foto_url": current_photo,
            }
            try:
                if foto is not None:
                    uploaded_url = upload_photo(foto, sku.strip() or nama.strip())
                    if uploaded_url:
                        payload["foto_url"] = uploaded_url
                save_product(payload, initial.get("id"))
                st.success("Berhasil disimpan!")
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menyimpan: {exc}")

    # Routing Halaman
    if page == "Ringkasan & Daftar Produk":
        if not products:
            st.info("Belum ada produk tersimpan. Buka menu **Tambah Produk**.")
        else:
            calculated_data = []
            for p in products:
                res = calculate(p)
                calculated_data.append({
                    "Nama": p.get("nama"),
                    "SKU": p.get("sku"),
                    "Harga Jual": rupiah(p.get("harga_jual", 0)),
                    "HPP Total": rupiah(res["hpp_total"]),
                    "Total Biaya": rupiah(res["total_biaya"]),
                    "Laba Bersih": rupiah(res["laba_bersih"]),
                    "Margin": f"{res['margin_pct']:.2f}%"
                })
            
            st.dataframe(pd.DataFrame(calculated_data), use_container_width=True)

    elif page == "Tambah Produk":
        st.markdown("### ➕ Tambah Produk Baru")
        product_form("add")

    elif page == "Edit / Hapus Produk":
        st.markdown("### ✏️ Edit atau Hapus Produk")
        if not products:
            st.warning("Data produk masih kosong.")
        else:
            prod_opts = {str(p["id"]): f"{p.get('nama')} - {p.get('sku', '')}" for p in products}
            selected_id = st.selectbox("Pilih produk yang ingin diedit/hapus", options=list(prod_opts.keys()), format_func=lambda x: prod_opts[x])
            
            sel_prod = products_by_id[selected_id]
            product_form("edit", sel_prod)
            
            st.divider()
            st.markdown("#### Hapus Produk")
            if st.button("🗑️ Hapus Produk Ini", type="secondary"):
                try:
                    supabase.table(TABLE_NAME).delete().eq("id", selected_id).execute()
                    st.success("Produk berhasil dihapus!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus: {e}")