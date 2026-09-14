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
# 2. KONFIGURASI TEMA, JINGGA & 1 TROLI BESAR DI TENGAH
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

    /* Background: Jingga Tipis + 1 Troli Belanja Besar di Tengah (No Repeat) */
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

# TAMPILAN JIKA BELUM LOGIN
if not st.session_state["logged_in"]:
    st.markdown(
        '<div class="main-title" style="text-align: center; margin-top: 40px;">🛒 Toko Management Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="main-subtitle" style="text-align: center;">Sistem Terproteksi. Silakan login atau ajukan akses ke Master Admin.</div>',
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
                log_user = st.text_input(
                    "Username / Akses ID", key="login_user"
                )
                log_pass = st.text_input(
                    "Password", type="password", key="login_pass"
                )

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
                                    st.warning(
                                        "⏳ Akun Anda masih berstatus PENDING. Silakan minta persetujuan Master Admin!"
                                    )
                                else:
                                    st.session_state["logged_in"] = True
                                    st.session_state["user_role"] = (
                                        user_data.get("role", "staff")
                                    )
                                    st.session_state["username"] = (
                                        user_data.get("username")
                                    )
                                    st.session_state["user_name"] = (
                                        user_data.get(
                                            "nama_lengkap", log_user
                                        )
                                    )
                                    st.rerun()
                        except Exception as e_auth:
                            st.error(f"Gagal verifikasi: {e_auth}")

            with tab_reg:
                st.markdown("##### Ajukan Akses Anggota Baru")
                reg_name = st.text_input("Nama Lengkap", key="reg_name")
                reg_user = st.text_input("Buat Username Baru", key="reg_user")
                reg_pass = st.text_input(
                    "Buat Password", type="password", key="reg_pass"
                )

                if st.button(
                    "Kirim Permintaan Akses", use_container_width=True
                ):
                    if (
                        not reg_name.strip()
                        or not reg_user.strip()
                        or not reg_pass.strip()
                    ):
                        st.warning("⚠️ Harap lengkapi semua kolom!")
                    else:
                        try:
                            cek = (
                                supabase.table("users_akses")
                                .select("id")
                                .eq("username", reg_user.strip())
                                .execute()
                            )
                            if cek.data:
                                st.error(
                                    "⚠️ Username sudah digunakan orang lain!"
                                )
                            else:
                                payload = {
                                    "username": reg_user.strip(),
                                    "password": reg_pass.strip(),
                                    "nama_lengkap": reg_name.strip(),
                                    "role": "staff",
                                    "status_akses": "pending",
                                }
                                supabase.table("users_akses").insert(
                                    payload
                                ).execute()
                                st.success(
                                    "✅ Permintaan akses terkirim! Hubungi Master Admin untuk konfirmasi."
                                )
                        except Exception as e_reg:
                            st.error(f"Gagal mendaftar: {e_reg}")
    st.stop()

# ==========================================
# HEADER UTAMA (SETELAH LOGIN)
# ==========================================
col_h1, col_h2 = st.columns([3.5, 1])
with col_h1:
    st.markdown(
        '<div class="main-title">🛒 Toko Management Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="main-subtitle">Pengguna Aktif: <b>{st.session_state["user_name"]}</b> | Role: <span style="color:#ea580c; font-weight:700;">{st.session_state["user_role"].upper()}</span></div>',
        unsafe_allow_html=True,
    )

with col_h2:
    st.write("")
    if st.button(
        "🚪 Keluar (Logout)",
        type="secondary",
        use_container_width=True,
    ):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["username"] = None
        st.session_state["user_name"] = None
        st.rerun()

# Menu Tab (Master Admin Mendapatkan Tab 3 Tambahan)
if st.session_state["user_role"] == "admin":
    tab1, tab2, tab3 = st.tabs(
        [
            "🧮 Tab 1: Kalkulator HPP & ROAS",
            "📦 Tab 2: Data Barang (Cloud)",
            "👥 Tab 3: Kelola Akses Tim (Master Admin)",
        ]
    )
else:
    tab1, tab2 = st.tabs(
        ["🧮 Tab 1: Kalkulator HPP & ROAS", "📦 Tab 2: Data Barang (Cloud)"]
    )

# ==========================================
# TAB 1: KALKULATOR
# ==========================================
with tab1:
    col_input, col_result = st.columns([1.05, 1.15], gap="large")

    with col_input:
        with st.container(border=True):
            st.markdown("#### 📌 Data Produk & Harga Pokok")
            nama_produk = st.text_input(
                "Nama Produk", placeholder="Contoh: Kemeja Linen Pria"
            )

            c1, c2 = st.columns(2)
            min_order = c1.number_input(
                "Minimum Order (Qty)",
                min_value=1,
                value=2,
                step=1,
                key="t1_mo",
            )
            modal_unit = c2.number_input(
                "Modal Produk / Unit (Rp)",
                min_value=0.0,
                value=2397.0,
                step=100.0,
                key="t1_mu",
            )

            total_modal = float(min_order * modal_unit)
            st.number_input(
                f"🔒 Total Modal Produk ({min_order} Pcs)",
                value=total_modal,
                disabled=True,
                format="%.0f",
            )

        with st.container(border=True):
            st.markdown("#### 🏷️ Penetapan Harga Jual")
            c_hj1, c_hj2 = st.columns(2)
            harga_jual_unit = c_hj1.number_input(
                "Harga Jual / Unit (Rp)",
                min_value=0.0,
                value=6500.0,
                step=500.0,
                key="t1_hju",
            )

            harga_jual_total = float(min_order * harga_jual_unit)
            c_hj2.number_input(
                f"🔒 Total Omset ({min_order} Pcs)",
                value=harga_jual_total,
                disabled=True,
                format="%.0f",
            )

        with st.container(border=True):
            st.markdown("#### ⚙️ Biaya Operasional & Komisi")
            c3, c4 = st.columns(2)
            biaya_proses = 1250.0
            c3.number_input(
                "🔒 Biaya Pemrosesan (Fixed)",
                value=biaya_proses,
                disabled=True,
                format="%.0f",
            )
            biaya_packing = c4.number_input(
                "Biaya Packing (Rp)",
                min_value=0.0,
                value=400.0,
                step=100.0,
                key="t1_bp",
            )

            c5, c6 = st.columns(2)
            biaya_ams_persen = c5.number_input(
                "Biaya AMS (%)",
                min_value=0.0,
                max_value=100.0,
                value=1.5,
                step=0.1,
                key="t1_ams",
            )
            biaya_mp_persen = c6.number_input(
                "Biaya Marketplace (%)",
                min_value=0.0,
                max_value=100.0,
                value=18.0,
                step=0.5,
                key="t1_mp",
            )

            target_margin = st.number_input(
                "Target Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                key="t1_tm",
            )

    # Rumus Hitungan
    nominal_ams = (biaya_ams_persen / 100.0) * harga_jual_total
    nominal_mp = (biaya_mp_persen / 100.0) * harga_jual_total
    total_beban_operasional = (
        biaya_proses + biaya_packing + nominal_ams + nominal_mp
    )
    total_hpp_beban = total_modal + total_beban_operasional

    laba_bersih_total = harga_jual_total - total_hpp_beban
    laba_bersih_unit = (
        laba_bersih_total / min_order if min_order > 0 else 0.0
    )
    margin_bersih_persen = (
        (laba_bersih_total / harga_jual_total * 100)
        if harga_jual_total > 0
        else 0
    )
    bep_roas = (
        harga_jual_total / laba_bersih_total if laba_bersih_total > 0 else 0.0
    )

    with col_result:
        with st.container(border=True):
            st.markdown("#### 📈 Ringkasan Performa Keuangan")
            m1, m2, m3 = st.columns(3)
            m1.metric(
                f"Laba Bersih ({min_order} Pcs)",
                f"Rp {laba_bersih_total:,.0f}",
                delta=f"Rp {laba_bersih_unit:,.0f} / pcs",
                delta_color="normal",
            )
            m2.metric(
                "Margin Bersih",
                f"{margin_bersih_persen:.2f}%",
                delta=f"{margin_bersih_persen - target_margin:.2f}% vs Target",
            )
            m3.metric(
                "BEP ROAS Iklan",
                f"{bep_roas:.2f}x" if bep_roas > 0 else "N/A (Rugi)",
            )

        with st.container(border=True):
            st.markdown(f"**Rincian Transaksi Paket ({min_order} Pcs):**")
            rincian_df = pd.DataFrame(
                {
                    "Komponen Biaya": [
                        f"1. Modal Pokok ({min_order} pcs @ Rp {modal_unit:,.0f})",
                        "2. Biaya Pemrosesan Pesanan (Fixed)",
                        "3. Biaya Packing",
                        f"4. Biaya AMS ({biaya_ams_persen}%)",
                        f"5. Biaya Marketplace ({biaya_mp_persen}%)",
                        "TOTAL HPP & OPERASIONAL",
                        f"TOTAL HARGA JUAL / OMSET ({min_order} pcs)",
                    ],
                    "Nominal": [
                        f"Rp {total_modal:,.0f}",
                        f"Rp {biaya_proses:,.0f}",
                        f"Rp {biaya_packing:,.0f}",
                        f"Rp {nominal_ams:,.0f}",
                        f"Rp {nominal_mp:,.0f}",
                        f"Rp {total_hpp_beban:,.0f}",
                        f"Rp {harga_jual_total:,.0f}",
                    ],
                }
            )
            st.table(rincian_df)

            if bep_roas > 0:
                st.info(
                    f"💡 **BEP ROAS ({bep_roas:.2f}x):** Setiap budget iklan **Rp 100.000**, wajib menghasilkan omzet minimal **Rp {bep_roas * 100000:,.0f}** agar tidak rugi."
                )
            else:
                st.error("⚠️ Beban melebihi harga jual (Margin Minus).")

            if st.button(
                "💾 Simpan ke Database Cloud",
                type="primary",
                use_container_width=True,
            ):
                if not nama_produk.strip():
                    st.warning("⚠️ Masukkan nama produk terlebih dahulu!")
                else:
                    insert_payload = {
                        "tanggal_input": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "nama_produk": nama_produk,
                        "min_order": int(min_order),
                        "modal_unit": float(modal_unit),
                        "total_modal": float(total_modal),
                        "biaya_packing": float(biaya_packing),
                        "ams_persen": float(biaya_ams_persen),
                        "mp_persen": float(biaya_mp_persen),
                        "harga_jual_unit": float(harga_jual_unit),
                        "harga_jual_total": float(harga_jual_total),
                        "target_margin": float(target_margin),
                        "total_hpp_beban": float(total_hpp_beban),
                        "laba_bersih_total": float(laba_bersih_total),
                        "laba_bersih_unit": float(laba_bersih_unit),
                        "margin_bersih_persen": float(margin_bersih_persen),
                        "bep_roas": float(bep_roas),
                        "image_url": "",
                    }
                    try:
                        supabase.table("produk").insert(
                            insert_payload
                        ).execute()
                        st.success(
                            f"✅ Produk '{nama_produk}' berhasil disimpan ke Cloud!"
                        )
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Gagal menyimpan data: {ex}")

# ==========================================
# TAB 2: DATA BARANG CLOUD
# ==========================================
with tab2:
    try:
        res = (
            supabase.table("produk")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        df_raw = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e_fetch:
        st.error(f"Gagal mengambil data dari Supabase: {e_fetch}")
        df_raw = pd.DataFrame()

    if df_raw.empty:
        st.info("Belum ada data barang di Cloud.")
    else:
        c_srch, c_sel = st.columns([1, 1])
        search_query = c_srch.text_input(
            "🔍 Cari Produk:", placeholder="Ketik nama produk..."
        ).strip()

        if search_query:
            df_filtered = df_raw[
                df_raw["nama_produk"]
                .astype(str)
                .str.lower()
                .str.contains(search_query.lower())
            ]
        else:
            df_filtered = df_raw

        display_df = pd.DataFrame()
        display_df["ID"] = df_filtered["id"]
        display_df["Nama Produk"] = df_filtered["nama_produk"]
        display_df["Min. Order"] = df_filtered["min_order"]
        display_df["Modal/Unit"] = df_filtered["modal_unit"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        display_df["Harga Jual/Unit"] = df_filtered["harga_jual_unit"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        display_df["Laba Bersih"] = df_filtered["laba_bersih_total"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        display_df["Margin (%)"] = df_filtered["margin_bersih_persen"].apply(
            lambda x: f"{float(x):.2f}%" if pd.notnull(x) else "-"
        )
        display_df["BEP ROAS"] = df_filtered["bep_roas"].apply(
            lambda x: f"{float(x):.2f}x" if pd.notnull(x) else "-"
        )

        with st.container(border=True):
            st.markdown(
                "**📋 Daftar Produk (Klik baris pada tabel untuk membuka Card):**"
            )
            event = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
            )

        selected_id = None
        selected_rows = (
            event.selection.rows if hasattr(event, "selection") else []
        )
        if len(selected_rows) > 0:
            selected_idx = selected_rows[0]
            selected_id = int(display_df.iloc[selected_idx]["ID"])
        else:
            options_dict = {
                f"ID {row['id']} - {row['nama_produk']}": int(row["id"])
                for _, row in df_filtered.iterrows()
            }
            pilihan = c_sel.selectbox(
                "Atau Pilih Produk dari Dropdown:",
                list(options_dict.keys()),
                index=0,
            )
            selected_id = options_dict[pilihan]

        row_data = df_raw[df_raw["id"] == selected_id].iloc[0]

        # Card Produk Detail
        with st.container(border=True):
            st.markdown(
                f"### 🎴 Card Produk: **{row_data['nama_produk']}** (ID: {selected_id})"
            )

            card_col_img, card_col_form = st.columns([1, 2], gap="large")

            with card_col_img:
                st.markdown("##### 🖼️ Foto Produk (Cloud)")
                current_img_url = (
                    str(row_data.get("image_url", ""))
                    if pd.notnull(row_data.get("image_url"))
                    else ""
                )

                if current_img_url and current_img_url.strip():
                    st.image(
                        current_img_url,
                        caption=row_data["nama_produk"],
                        use_container_width=True,
                    )
                else:
                    st.info("📷 Belum ada foto di Cloud.")

                uploaded_file = st.file_uploader(
                    "Unggah / Ganti Foto ke Cloud",
                    type=["png", "jpg", "jpeg"],
                    key=f"uploader_{selected_id}",
                )

            with card_col_form:
                st.markdown("##### ✏️ Edit Parameter Produk")

                e_nama = st.text_input(
                    "Nama Produk",
                    value=str(row_data["nama_produk"]),
                    key=f"e_nama_{selected_id}",
                )

                c_e1, c_e2 = st.columns(2)
                e_min_order = c_e1.number_input(
                    "Minimum Order (Qty)",
                    min_value=1,
                    value=int(row_data["min_order"]),
                    step=1,
                    key=f"e_mo_{selected_id}",
                )
                e_modal_unit = c_e2.number_input(
                    "Modal Aktif / Unit (Rp)",
                    min_value=0.0,
                    value=float(row_data["modal_unit"]),
                    step=100.0,
                    key=f"e_mu_{selected_id}",
                )

                c_e3, c_e4 = st.columns(2)
                e_harga_jual_unit = c_e3.number_input(
                    "Harga Jual / Unit (Rp)",
                    min_value=0.0,
                    value=float(row_data.get("harga_jual_unit", 0.0)),
                    step=500.0,
                    key=f"e_hju_{selected_id}",
                )
                e_packing = c_e4.number_input(
                    "Biaya Packing (Rp)",
                    min_value=0.0,
                    value=float(row_data.get("biaya_packing", 400.0)),
                    step=100.0,
                    key=f"e_pack_{selected_id}",
                )

                c_e5, c_e6, c_e7 = st.columns(3)
                e_ams = c_e5.number_input(
                    "Biaya AMS (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row_data.get("ams_persen", 1.5)),
                    step=0.1,
                    key=f"e_ams_{selected_id}",
                )
                e_mp = c_e6.number_input(
                    "Biaya Marketplace (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row_data.get("mp_persen", 18.0)),
                    step=0.5,
                    key=f"e_mp_{selected_id}",
                )
                e_margin_target = c_e7.number_input(
                    "Target Margin (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row_data.get("target_margin", 20.0)),
                    step=1.0,
                    key=f"e_tm_{selected_id}",
                )

                e_total_modal = e_min_order * e_modal_unit
                e_total_omset = e_min_order * e_harga_jual_unit
                e_nom_ams = (e_ams / 100.0) * e_total_omset
                e_nom_mp = (e_mp / 100.0) * e_total_omset
                e_biaya_proses = 1250.0
                e_total_beban = (
                    e_total_modal
                    + e_biaya_proses
                    + e_packing
                    + e_nom_ams
                    + e_nom_mp
                )
                e_laba_total = e_total_omset - e_total_beban
                e_laba_unit = (
                    e_laba_total / e_min_order if e_min_order > 0 else 0.0
                )
                e_margin_persen = (
                    (e_laba_total / e_total_omset * 100)
                    if e_total_omset > 0
                    else 0
                )
                e_bep_roas = (
                    e_total_omset / e_laba_total if e_laba_total > 0 else 0.0
                )

                st.markdown("**Performa Terkalkulasi:**")
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("Total Modal", f"Rp {e_total_modal:,.0f}")
                col_m2.metric("Total Omset", f"Rp {e_total_omset:,.0f}")
                col_m3.metric(
                    "Laba Bersih",
                    f"Rp {e_laba_total:,.0f}",
                    f"{e_margin_persen:.1f}%",
                )
                col_m4.metric(
                    "BEP ROAS",
                    f"{e_bep_roas:.2f}x" if e_bep_roas > 0 else "Rugi",
                )

                btn_save, btn_del = st.columns([2, 1])
                if btn_save.button(
                    "💾 Simpan Perubahan ke Cloud",
                    type="primary",
                    use_container_width=True,
                    key=f"btn_save_{selected_id}",
                ):
                    final_img_url = current_img_url
                    if uploaded_file is not None:
                        ext = uploaded_file.name.split(".")[-1]
                        file_name = f"prod_{selected_id}_{int(datetime.now().timestamp())}.{ext}"
                        try:
                            file_bytes = uploaded_file.getvalue()
                            supabase.storage.from_(BUCKET_NAME).upload(
                                path=file_name,
                                file=file_bytes,
                                file_options={
                                    "content-type": uploaded_file.type,
                                    "upsert": "true",
                                },
                            )
                            final_img_url = supabase.storage.from_(
                                BUCKET_NAME
                            ).get_public_url(file_name)
                        except Exception as err_up:
                            st.warning(f"Catatan foto: {err_up}")

                    update_payload = {
                        "nama_produk": e_nama,
                        "min_order": int(e_min_order),
                        "modal_unit": float(e_modal_unit),
                        "total_modal": float(e_total_modal),
                        "biaya_packing": float(e_packing),
                        "ams_persen": float(e_ams),
                        "mp_persen": float(e_mp),
                        "harga_jual_unit": float(e_harga_jual_unit),
                        "harga_jual_total": float(e_total_omset),
                        "target_margin": float(e_margin_target),
                        "total_hpp_beban": float(e_total_beban),
                        "laba_bersih_total": float(e_laba_total),
                        "laba_bersih_unit": float(e_laba_unit),
                        "margin_bersih_persen": float(e_margin_persen),
                        "bep_roas": float(e_bep_roas),
                        "image_url": final_img_url,
                    }

                    try:
                        supabase.table("produk").update(update_payload).eq(
                            "id", selected_id
                        ).execute()
                        st.success(
                            f"✅ Data produk '{e_nama}' berhasil diperbarui di Cloud!"
                        )
                        st.rerun()
                    except Exception as ex_up:
                        st.error(f"Gagal memperbarui: {ex_up}")

                if btn_del.button(
                    "🗑️ Hapus Produk",
                    type="secondary",
                    use_container_width=True,
                    key=f"btn_del_{selected_id}",
                ):
                    try:
                        supabase.table("riwayat_modal").delete().eq(
                            "produk_id", selected_id
                        ).execute()
                        supabase.table("produk").delete().eq(
                            "id", selected_id
                        ).execute()
                        st.warning(
                            f"Produk ID {selected_id} dihapus dari Cloud."
                        )
                        st.rerun()
                    except Exception as ex_del:
                        st.error(f"Gagal menghapus: {ex_del}")

        # Sub-Tabel Variasi Modal
        with st.container(border=True):
            st.markdown(
                f"#### 📑 Sub-Tabel Variasi Modal: **{row_data['nama_produk']}**"
            )

            try:
                res_m = (
                    supabase.table("riwayat_modal")
                    .select("*")
                    .eq("produk_id", selected_id)
                    .order("id", desc=True)
                    .execute()
                )
                df_modal = (
                    pd.DataFrame(res_m.data) if res_m.data else pd.DataFrame()
                )
            except Exception:
                df_modal = pd.DataFrame()

            col_tabel_modal, col_form_modal = st.columns(
                [1.3, 1], gap="medium"
            )

            with col_tabel_modal:
                if df_modal.empty:
                    st.info(
                        "Belum ada variasi modal tambahan. Tambahkan catatan di panel kanan."
                    )
                else:
                    tampil_modal = pd.DataFrame()
                    tampil_modal["ID"] = df_modal["id"]
                    tampil_modal["Tanggal"] = df_modal["tanggal_update"]
                    tampil_modal["Label Modal (Custom)"] = df_modal[
                        "nama_keterangan"
                    ]
                    tampil_modal["Nominal (Rp)"] = df_modal[
                        "nominal_modal"
                    ].apply(lambda x: f"Rp {float(x):,.0f}")

                    st.dataframe(
                        tampil_modal, use_container_width=True, hide_index=True
                    )

                    c_sel_m, c_btn_m, c_btn_del = st.columns([1.4, 1, 0.7])
                    pilihan_modal_dict = {
                        f"{r['nama_keterangan']} (Rp {float(r['nominal_modal']):,.0f})": (
                            r["id"],
                            r["nominal_modal"],
                        )
                        for _, r in df_modal.iterrows()
                    }

                    pilih_entry = c_sel_m.selectbox(
                        "Pilih Modal:",
                        list(pilihan_modal_dict.keys()),
                        key=f"sel_m_{selected_id}",
                    )
                    id_modal_terpilih, modal_nilai_terpilih = (
                        pilihan_modal_dict[pilih_entry]
                    )

                    if c_btn_m.button(
                        "⚡ Jadikan Modal Utama",
                        use_container_width=True,
                        key=f"btn_apply_{selected_id}",
                    ):
                        try:
                            supabase.table("produk").update(
                                {"modal_unit": float(modal_nilai_terpilih)}
                            ).eq("id", selected_id).execute()
                            st.success(
                                f"Modal utama berhasil diubah ke Rp {float(modal_nilai_terpilih):,.0f}!"
                            )
                            st.rerun()
                        except Exception as ex_app:
                            st.error(f"Gagal menerapkan modal: {ex_app}")

                    if c_btn_del.button(
                        "❌ Hapus",
                        use_container_width=True,
                        key=f"btn_del_mod_{selected_id}",
                    ):
                        try:
                            supabase.table("riwayat_modal").delete().eq(
                                "id", id_modal_terpilih
                            ).execute()
                            st.warning("Data modal dihapus.")
                            st.rerun()
                        except Exception as ex_del_m:
                            st.error(f"Gagal menghapus: {ex_del_m}")

            with col_form_modal:
                st.markdown("**➕ Tambah Catatan Modal Baru**")
                label_modal_baru = st.text_input(
                    "Label / Keterangan",
                    placeholder="Contoh: Supplier Batch 2",
                    key=f"lbl_m_{selected_id}",
                )
                nominal_modal_baru = st.number_input(
                    "Nominal (Rp)",
                    min_value=0.0,
                    value=float(row_data["modal_unit"]),
                    step=100.0,
                    key=f"nom_m_{selected_id}",
                )
                terapkan_langsung = st.checkbox(
                    "Langsung jadikan modal aktif?",
                    value=False,
                    key=f"chk_apply_{selected_id}",
                )

                if st.button(
                    "Simpan Variasi Modal",
                    type="primary",
                    use_container_width=True,
                    key=f"btn_add_modal_{selected_id}",
                ):
                    if not label_modal_baru.strip():
                        st.warning("⚠️ Masukkan nama label atau keterangan!")
                    else:
                        waktu_sekarang = datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        )
                        payload_m = {
                            "produk_id": selected_id,
                            "tanggal_update": waktu_sekarang,
                            "nama_keterangan": label_modal_baru,
                            "nominal_modal": float(nominal_modal_baru),
                        }
                        try:
                            supabase.table("riwayat_modal").insert(
                                payload_m
                            ).execute()
                            if terapkan_langsung:
                                supabase.table("produk").update(
                                    {"modal_unit": float(nominal_modal_baru)}
                                ).eq("id", selected_id).execute()
                            st.success(f"✅ Variasi '{label_modal_baru}' tersimpan!")
                            st.rerun()
                        except Exception as ex_in_m:
                            st.error(f"Gagal menambah: {ex_in_m}")

        # Download CSV
        st.markdown("---")
        csv_data = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data CSV",
            data=csv_data,
            file_name="database_produk_cloud.csv",
            mime="text/csv",
        )

# ==========================================
# TAB 3: KELOLA AKSES TIM (KHUSUS MASTER ADMIN)
# ==========================================
if st.session_state["user_role"] == "admin":
    with tab3:
        st.subheader("👥 Manajemen Hak Akses Tim & Pengguna")
        st.info(
            "💡 Sebagai Master Admin, Anda dapat menyetujui pendaftar baru, mencabut akses, atau menghapus akun anggota tim."
        )

        try:
            res_users = (
                supabase.table("users_akses")
                .select("*")
                .order("id", desc=False)
                .execute()
            )
            df_users = (
                pd.DataFrame(res_users.data)
                if res_users.data
                else pd.DataFrame()
            )
        except Exception:
            df_users = pd.DataFrame()

        if df_users.empty:
            st.warning("Belum ada data pengguna.")
        else:
            with st.container(border=True):
                st.markdown("##### 📋 Daftar Seluruh Akun Terdaftar")
                tampil_users = pd.DataFrame()
                tampil_users["ID"] = df_users["id"]
                tampil_users["Nama Lengkap"] = df_users["nama_lengkap"]
                tampil_users["Username"] = df_users["username"]
                tampil_users["Role"] = df_users["role"].str.upper()
                tampil_users["Status Akses"] = df_users["status_akses"].apply(
                    lambda x: (
                        "🟢 DISETUJUI (Aktif)"
                        if x == "approved"
                        else "🟡 MENUNGGU PERSETUJUAN (Pending)"
                    )
                )

                st.dataframe(
                    tampil_users, use_container_width=True, hide_index=True
                )

            # Panel Eksekusi Persetujuan
            with st.container(border=True):
                st.markdown("##### ⚙️ Aksi Persetujuan & Kontrol Akun")
                list_user_non_admin = df_users[
                    df_users["username"] != st.session_state["username"]
                ]

                if list_user_non_admin.empty:
                    st.info(
                        "Belum ada anggota tim lain yang mendaftar. Anggota baru bisa mendaftar lewat tab 'Minta Akses (Daftar)' di layar login."
                    )
                else:
                    user_dict = {
                        f"{r['nama_lengkap']} (@{r['username']}) - Status: {r['status_akses'].upper()}": r[
                            "id"
                        ]
                        for _, r in list_user_non_admin.iterrows()
                    }

                    pilih_user_label = st.selectbox(
                        "Pilih Anggota Tim:", list(user_dict.keys())
                    )
                    id_target = user_dict[pilih_user_label]

                    b_app, b_rev, b_del_u = st.columns(3)

                    if b_app.button(
                        "✅ Beri Akses (Approve)",
                        type="primary",
                        use_container_width=True,
                    ):
                        supabase.table("users_akses").update(
                            {"status_akses": "approved"}
                        ).eq("id", id_target).execute()
                        st.success("Akses berhasil diberikan! Pengguna kini bisa login.")
                        st.rerun()

                    if b_rev.button(
                        "🔒 Kunci / Pending Akses",
                        use_container_width=True,
                    ):
                        supabase.table("users_akses").update(
                            {"status_akses": "pending"}
                        ).eq("id", id_target).execute()
                        st.warning("Akses dikunci kembali menjadi Pending.")
                        st.rerun()

                    if b_del_u.button(
                        "🗑️ Hapus Akun",
                        use_container_width=True,
                    ):
                        supabase.table("users_akses").delete().eq(
                            "id", id_target
                        ).execute()
                        st.error("Akun berhasil dihapus dari sistem.")
                        st.rerun()