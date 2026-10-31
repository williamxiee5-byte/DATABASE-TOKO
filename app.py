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
      '<div class="main-title" style="text-align: center; margin-top:'
      ' 40px;">🛒 Toko Management Dashboard</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="main-subtitle" style="text-align: center;">Sistem'
      " Terproteksi. Silakan login atau ajukan akses ke Master Admin.</div>",
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
                  st.warning(
                      "⏳ Akun Anda masih berstatus PENDING. Silakan minta"
                      " persetujuan Master Admin!"
                  )
                else:
                  st.session_state["logged_in"] = True
                  st.session_state["user_role"] = user_data.get("role", "staff")
                  st.session_state["username"] = user_data.get("username")
                  st.session_state["user_name"] = user_data.get(
                      "nama_lengkap", log_user
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

        if st.button("Kirim Permintaan Akses", use_container_width=True):
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
                st.error("⚠️ Username sudah digunakan orang lain!")
              else:
                payload = {
                    "username": reg_user.strip(),
                    "password": reg_pass.strip(),
                    "nama_lengkap": reg_name.strip(),
                    "role": "staff",
                    "status_akses": "pending",
                }
                supabase.table("users_akses").insert(payload).execute()
                st.success(
                    "✅ Permintaan akses terkirim! Hubungi Master Admin untuk"
                    " konfirmasi."
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
      '<div class="main-subtitle">Pengguna Aktif:'
      f' <b>{st.session_state["user_name"]}</b> | Role: <span'
      ' style="color:#ea580c;'
      f' font-weight:700;">{st.session_state["user_role"].upper()}</span></div>',
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

# Menu Tab
if st.session_state["user_role"] == "admin":
  tab1, tab2, tab3 = st.tabs([
      "🧮 Tab 1: Kalkulator HPP & ROAS",
      "📦 Tab 2: Data Barang (Cloud)",
      "👥 Tab 3: Kelola Akses Tim (Master Admin)",
  ])
else:
  tab1, tab2 = st.tabs(
      ["🧮 Tab 1: Kalkulator HPP & ROAS", "📦 Tab 2: Data Barang (Cloud)"]
  )

# ==========================================
# TAB 1: KALKULATOR HPP & ROAS
# ==========================================
with tab1:
  col_input, col_result = st.columns([1.1, 1.15], gap="large")

  with col_input:
    with st.container(border=True):
      st.markdown("#### 📌 Data Pokok Produk")
      nama_produk = st.text_input(
          "Nama Produk", placeholder="Contoh: Kemeja Linen Pria"
      )

      modal_unit = st.number_input(
          "Modal Produk / Unit / HPP (Rp)",
          min_value=0.0,
          value=1200.0,
          step=100.0,
          key="t1_mu",
      )

    with st.container(border=True):
      st.markdown("#### 📦 Skema Grosir & Minimal Order (Tier Pricing)")
      st.caption(
          "💡 **Tips:** Klik **'+'** di bawah untuk menambah tier. Untuk"
          " menghapus baris, centang kotak di sisi kiri baris lalu tekan"
          " **Delete** di keyboard."
      )

      default_tiers = pd.DataFrame([
          {"min_order": 1, "harga_jual": 6500.0},
      ])

      editor_tier = st.data_editor(
          default_tiers,
          num_rows="dynamic",
          column_config={
              "min_order": st.column_config.NumberColumn(
                  "Min. Order (Qty)",
                  help="Minimal pcs pembelian",
                  min_value=1,
                  step=1,
                  required=True,
              ),
              "harga_jual": st.column_config.NumberColumn(
                  "Harga Jual / Unit (Rp)",
                  help="Harga satuan pada tier ini",
                  min_value=0.0,
                  step=500.0,
                  format="Rp %.0f",
                  required=True,
              ),
          },
          use_container_width=True,
          hide_index=True,
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

  if not editor_tier.empty:
    clean_tiers = editor_tier.dropna().copy()
    clean_tiers = clean_tiers[clean_tiers["harga_jual"] > 0]
  else:
    clean_tiers = pd.DataFrame()

  with col_result:
    with st.container(border=True):
      st.markdown("#### 📈 Ringkasan Performa Keuangan")

      if not clean_tiers.empty:
        tier_pilihan_list = [
            f"Min {int(r['min_order'])} Pcs (@ Rp {float(r['harga_jual']):,.0f})"
            for _, r in clean_tiers.iterrows()
        ]
        tier_terpilih_str = st.radio(
            "Pilih Skema Tier yang Ingin Disimulasikan:",
            tier_pilihan_list,
            horizontal=True,
        )

        pilihan_idx = tier_pilihan_list.index(tier_terpilih_str)
        baris_terpilih = clean_tiers.iloc[pilihan_idx]
        cur_min_order = int(baris_terpilih["min_order"])
        cur_harga_jual_unit = float(baris_terpilih["harga_jual"])
      else:
        cur_min_order = 1
        cur_harga_jual_unit = 0.0

      cur_total_modal = float(cur_min_order * modal_unit)
      cur_total_omset = float(cur_min_order * cur_harga_jual_unit)

      cur_nominal_ams = (biaya_ams_persen / 100.0) * cur_total_omset
      cur_nominal_mp = (biaya_mp_persen / 100.0) * cur_total_omset
      cur_total_beban = (
          cur_total_modal
          + biaya_proses
          + biaya_packing
          + cur_nominal_ams
          + cur_nominal_mp
      )

      cur_laba_total = cur_total_omset - cur_total_beban
      cur_laba_unit = (
          cur_laba_total / cur_min_order if cur_min_order > 0 else 0.0
      )
      cur_margin_persen = (
          (cur_laba_total / cur_total_omset * 100) if cur_total_omset > 0 else 0
      )
      cur_bep_roas = (
          cur_total_omset / cur_laba_total if cur_laba_total > 0 else 0.0
      )

      st.markdown(f"**Hasil Perhitungan (Min {cur_min_order} Pcs):**")
      m1, m2, m3 = st.columns(3)
      m1.metric(
          f"Laba Bersih ({cur_min_order} Pcs)",
          f"Rp {cur_laba_total:,.0f}",
          delta=f"Rp {cur_laba_unit:,.0f} / pcs",
          delta_color="normal",
      )
      m2.metric(
          "Margin Bersih",
          f"{cur_margin_persen:.2f}%",
          delta=f"{cur_margin_persen - target_margin:.2f}% vs Target",
      )
      m3.metric(
          "BEP ROAS Iklan",
          f"{cur_bep_roas:.2f}x" if cur_bep_roas > 0 else "N/A (Rugi)",
      )

    with st.container(border=True):
      st.markdown(f"**Rincian Transaksi (Min {cur_min_order} Pcs):**")
      rincian_df = pd.DataFrame({
          "Komponen Biaya": [
              f"1. Modal Pokok ({cur_min_order} pcs @ Rp {modal_unit:,.0f})",
              "2. Biaya Pemrosesan Pesanan (Fixed)",
              "3. Biaya Packing",
              f"4. Biaya AMS ({biaya_ams_persen}%)",
              f"5. Biaya Marketplace ({biaya_mp_persen}%)",
              "TOTAL HPP & OPERASIONAL",
              f"TOTAL HARGA JUAL / OMSET ({cur_min_order} pcs)",
          ],
          "Nominal": [
              f"Rp {cur_total_modal:,.0f}",
              f"Rp {biaya_proses:,.0f}",
              f"Rp {biaya_packing:,.0f}",
              f"Rp {cur_nominal_ams:,.0f}",
              f"Rp {cur_nominal_mp:,.0f}",
              f"Rp {cur_total_beban:,.0f}",
              f"Rp {cur_total_omset:,.0f}",
          ],
      })
      st.table(rincian_df)

      if cur_bep_roas > 0:
        target_omset_bep = cur_bep_roas * 100000
        st.info(
            f"💡 **BEP ROAS ({cur_bep_roas:.2f}x):** Setiap budget iklan **Rp"
            f" 100.000**, wajib menghasilkan omzet minimal **Rp"
            f" {target_omset_bep:,.0f}** agar tidak rugi."
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
        elif clean_tiers.empty:
          st.warning(
              "⚠️ Masukkan minimal satu baris tier order yang harganya > 0!"
          )
        else:
          first_tier = clean_tiers.iloc[0]
          b_mo = int(first_tier["min_order"])
          b_hj = float(first_tier["harga_jual"])
          b_tm = float(b_mo * modal_unit)
          b_to = float(b_mo * b_hj)
          b_ams = (biaya_ams_persen / 100.0) * b_to
          b_mp = (biaya_mp_persen / 100.0) * b_to
          b_beban = b_tm + biaya_proses + biaya_packing + b_ams + b_mp
          b_laba = b_to - b_beban
          b_laba_u = b_laba / b_mo if b_mo > 0 else 0.0
          b_margin = (b_laba / b_to * 100) if b_to > 0 else 0.0
          b_roas = b_to / b_laba if b_laba > 0 else 0.0

          insert_payload = {
              "tanggal_input": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "nama_produk": nama_produk.strip(),
              "min_order": b_mo,
              "modal_unit": float(modal_unit),
              "total_modal": b_tm,
              "biaya_packing": float(biaya_packing),
              "ams_persen": float(biaya_ams_persen),
              "mp_persen": float(biaya_mp_persen),
              "harga_jual_unit": b_hj,
              "harga_jual_total": b_to,
              "target_margin": float(target_margin),
              "total_hpp_beban": b_beban,
              "laba_bersih_total": b_laba,
              "laba_bersih_unit": b_laba_u,
              "margin_bersih_persen": b_margin,
              "bep_roas": b_roas,
              "image_url": "",
          }
          try:
            res_p = supabase.table("produk").insert(insert_payload).execute()
            if res_p.data:
              new_product_id = res_p.data[0]["id"]

              list_tiers = []
              for _, r in clean_tiers.iterrows():
                list_tiers.append({
                    "product_id": new_product_id,
                    "min_order": int(r["min_order"]),
                    "harga_jual": float(r["harga_jual"]),
                })

              if list_tiers:
                supabase.table("product_tiers").insert(list_tiers).execute()

              supabase.table("riwayat_harga_produk").insert({
                  "produk_id": new_product_id,
                  "tanggal_perubahan": datetime.now().strftime(
                      "%Y-%m-%d %H:%M"
                  ),
                  "modal_lama": float(modal_unit),
                  "modal_baru": float(modal_unit),
                  "harga_jual_lama": float(b_hj),
                  "harga_jual_baru": float(b_hj),
                  "keterangan": "Inisialisasi Produk Baru",
                  "diubah_oleh": st.session_state.get("user_name", "Staff"),
              }).execute()

              st.success(
                  f"✅ Produk '{nama_produk}' berhasil disimpan ke Cloud"
                  f" beserta {len(list_tiers)} skema tier order!"
              )
              st.rerun()
          except Exception as ex:
            st.error(f"Gagal menyimpan data: {ex}")

# ==========================================
# TAB 2: DATA BARANG CLOUD
# ==========================================
with tab2:
  try:
    res = supabase.table("produk").select("*").order("id", desc=True).execute()
    df_raw = pd.DataFrame(res.data) if res.data else pd.DataFrame()
  except Exception as e_fetch:
    st.error(f"Gagal mengambil data dari Supabase: {e_fetch}")
    df_raw = pd.DataFrame()

  if df_raw.empty:
    st.info("Belum ada data barang di Cloud.")
  else:
    try:
      res_tiers = supabase.table("product_tiers").select("*").execute()
      df_tiers_all = (
          pd.DataFrame(res_tiers.data) if res_tiers.data else pd.DataFrame()
      )
    except Exception:
      df_tiers_all = pd.DataFrame()

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

    rows_expanded = []
    for _, prod in df_filtered.iterrows():
      pid = prod["id"]
      p_nama = prod["nama_produk"]
      p_modal = float(prod.get("modal_unit", 0.0))
      p_pack = float(prod.get("biaya_packing", 400.0))
      p_ams = float(prod.get("ams_persen", 1.5))
      p_mp = float(prod.get("mp_persen", 18.0))
      biaya_proc = 1250.0

      matched_tiers = pd.DataFrame()
      if not df_tiers_all.empty and "product_id" in df_tiers_all.columns:
        matched_tiers = df_tiers_all[
            df_tiers_all["product_id"] == pid
        ].sort_values("min_order")

      if not matched_tiers.empty:
        for _, tr in matched_tiers.iterrows():
          t_mo = int(tr["min_order"])
          t_hj = float(tr["harga_jual"])
          t_modal_total = t_mo * p_modal
          t_omset = t_mo * t_hj
          t_nom_ams = (p_ams / 100.0) * t_omset
          t_nom_mp = (p_mp / 100.0) * t_omset
          t_beban = t_modal_total + biaya_proc + p_pack + t_nom_ams + t_nom_mp
          t_laba = t_omset - t_beban
          t_margin = (t_laba / t_omset * 100) if t_omset > 0 else 0.0
          t_bep = t_omset / t_laba if t_laba > 0 else 0.0

          rows_expanded.append({
              "ID": pid,
              "Nama Produk": p_nama,
              "Min. Order": t_mo,
              "Modal/Unit": f"Rp {p_modal:,.0f}",
              "Harga Jual/Unit": f"Rp {t_hj:,.0f}",
              "Laba Bersih": f"Rp {t_laba:,.0f}",
              "Margin (%)": f"{t_margin:.2f}%",
              "BEP ROAS": f"{t_bep:.2f}x" if t_bep > 0 else "Rugi",
              # Nilai numerik murni untuk parsing card
              "_num_modal": p_modal,
              "_num_hj": t_hj,
              "_num_laba": t_laba,
              "_num_margin": t_margin,
              "_num_bep": t_bep,
          })
      else:
        p_mo = int(prod.get("min_order", 1))
        p_hj = float(prod.get("harga_jual_unit", 0.0))
        p_laba = float(prod.get("laba_bersih_total", 0.0))
        p_margin = float(prod.get("margin_bersih_persen", 0.0))
        p_bep = float(prod.get("bep_roas", 0.0))

        rows_expanded.append({
            "ID": pid,
            "Nama Produk": p_nama,
            "Min. Order": p_mo,
            "Modal/Unit": f"Rp {p_modal:,.0f}",
            "Harga Jual/Unit": f"Rp {p_hj:,.0f}",
            "Laba Bersih": f"Rp {p_laba:,.0f}",
            "Margin (%)": f"{p_margin:.2f}%",
            "BEP ROAS": f"{p_bep:.2f}x" if p_bep > 0 else "Rugi",
            "_num_modal": p_modal,
            "_num_hj": p_hj,
            "_num_laba": p_laba,
            "_num_margin": p_margin,
            "_num_bep": p_bep,
        })

    display_all_df = pd.DataFrame(rows_expanded)
    # Tampilkan kolom tabel tanpa kolom numerik helper
    table_show_df = display_all_df[[
        "ID",
        "Nama Produk",
        "Min. Order",
        "Modal/Unit",
        "Harga Jual/Unit",
        "Laba Bersih",
        "Margin (%)",
        "BEP ROAS",
    ]]

    with st.container(border=True):
      st.markdown(
          "**📋 Daftar Produk & Seluruh Skema Grosir (Klik/centang baris untuk"
          " melihat Card Performa):**"
      )
      event = st.dataframe(
          table_show_df,
          use_container_width=True,
          hide_index=True,
          on_select="rerun",
          selection_mode="single-row",
      )

    selected_id = None
    selected_row_data = None
    selected_rows = event.selection.rows if hasattr(event, "selection") else []

    if len(selected_rows) > 0:
      selected_idx = selected_rows[0]
      selected_row_data = display_all_df.iloc[selected_idx]
      selected_id = int(selected_row_data["ID"])
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
      matches = display_all_df[display_all_df["ID"] == selected_id]
      if not matches.empty:
        selected_row_data = matches.iloc[0]

    row_data = df_raw[df_raw["id"] == selected_id].iloc[0]

    # ==========================================
    # KARTU RINGKASAN PERFORMA PRODUK (CARD ALA TAB 1)
    # ==========================================
    if selected_row_data is not None:
      current_img_url = (
          str(row_data.get("image_url", ""))
          if pd.notnull(row_data.get("image_url"))
          else ""
      )

      with st.container(border=True):
        col_c_img, col_c_info = st.columns([1, 2.7], gap="large")

        with col_c_img:
          if current_img_url and current_img_url.strip():
            st.image(
                current_img_url,
                caption=selected_row_data["Nama Produk"],
                use_container_width=True,
            )
          else:
            st.markdown(
                """
                <div style="height: 190px; border-radius: 14px; border: 2px dashed rgba(251, 146, 60, 0.4); 
                            display: flex; flex-direction: column; align-items: center; justify-content: center; 
                            background-color: rgba(255, 247, 237, 0.6); color: #c2410c;">
                    <div style="font-size: 2.8rem; margin-bottom: 4px;">🖼️</div>
                    <div style="font-size: 0.85rem; font-weight: 600;">Belum Ada Foto</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_c_info:
          st.markdown(
              f'<div class="card-product-title">{selected_row_data["Nama Produk"]}</div>',
              unsafe_allow_html=True,
          )
          st.markdown(
              '<div class="card-product-sub">ID Produk: '
              f'<b>{selected_id}</b> &nbsp;|&nbsp; Target Tier: <span'
              ' style="background-color:#fed7aa; color:#9a3412; padding: 2px'
              ' 8px; border-radius: 6px; font-weight:700;">Min'
              f' {selected_row_data["Min. Order"]} Pcs</span></div>',
              unsafe_allow_html=True,
          )

          # Baris 1: Min Order, Modal Unit, Harga Jual
          k1, k2, k3 = st.columns(3)
          k1.metric(
              "📦 MIN. ORDER", f"{selected_row_data['Min. Order']} Pcs"
          )
          k2.metric("💰 MODAL / UNIT", selected_row_data["Modal/Unit"])
          k3.metric("🏷️ HARGA JUAL", selected_row_data["Harga Jual/Unit"])

          st.write("")
          # Baris 2: Laba Bersih, Margin (%), BEP ROAS
          k4, k5, k6 = st.columns(3)
          k4.metric(
              "📈 LABA BERSIH",
              selected_row_data["Laba Bersih"],
              delta=f"Paket {selected_row_data['Min. Order']} pcs",
              delta_color="normal",
          )
          k5.metric(
              "📊 MARGIN (%)",
              selected_row_data["Margin (%)"],
              delta=(
                  f"{float(selected_row_data['_num_margin']) - float(row_data.get('target_margin', 20.0)):.2f}%"
                  " vs Target"
              ),
          )
          k6.metric("🎯 BEP ROAS", selected_row_data["BEP ROAS"])

    # Card Edit Parameter Produk
    with st.container(border=True):
      st.markdown(
          f"### ⚙️ Edit & Kelola Produk: **{row_data['nama_produk']}** (ID:"
          f" {selected_id})"
      )

      card_col_img, card_col_form = st.columns([1, 2], gap="large")

      with card_col_img:
        st.markdown("##### 🖼️ Upload / Ganti Foto Produk")
        current_img_url = (
            str(row_data.get("image_url", ""))
            if pd.notnull(row_data.get("image_url"))
            else ""
        )

        uploaded_file = st.file_uploader(
            "Unggah File Foto",
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
            "Minimum Order Acuan (Qty)",
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
            (e_laba_total / e_total_omset * 100) if e_total_omset > 0 else 0
        )
        e_bep_roas = (
            e_total_omset / e_laba_total if e_laba_total > 0 else 0.0
        )

        st.markdown("**Performa Terkalkulasi (Acuan):**")
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
            file_name = (
                f"prod_{selected_id}_{int(datetime.now().timestamp())}.{ext}"
            )
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
              final_img_url = supabase.storage.from_(BUCKET_NAME).get_public_url(
                  file_name
              )
            except Exception as err_up:
              st.warning(f"Catatan foto: {err_up}")

          modal_lama = float(row_data["modal_unit"])
          harga_lama = float(row_data.get("harga_jual_unit", 0.0))
          modal_berubah = modal_lama != float(e_modal_unit)
          harga_berubah = harga_lama != float(e_harga_jual_unit)

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

            if modal_berubah or harga_berubah:
              ket_list = []
              if modal_berubah:
                ket_list.append(
                    f"Modal: Rp {modal_lama:,.0f} ➔ Rp {float(e_modal_unit):,.0f}"
                )
              if harga_berubah:
                ket_list.append(
                    f"Harga: Rp {harga_lama:,.0f} ➔ Rp"
                    f" {float(e_harga_jual_unit):,.0f}"
                )

              history_payload = {
                  "produk_id": selected_id,
                  "tanggal_perubahan": datetime.now().strftime(
                      "%Y-%m-%d %H:%M"
                  ),
                  "modal_lama": modal_lama,
                  "modal_baru": float(e_modal_unit),
                  "harga_jual_lama": harga_lama,
                  "harga_jual_baru": float(e_harga_jual_unit),
                  "keterangan": " | ".join(ket_list),
                  "diubah_oleh": st.session_state.get("user_name", "Staff"),
              }
              supabase.table("riwayat_harga_produk").insert(
                  history_payload
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
            supabase.table("product_tiers").delete().eq(
                "product_id", selected_id
            ).execute()
            supabase.table("riwayat_harga_produk").delete().eq(
                "produk_id", selected_id
            ).execute()
            supabase.table("produk").delete().eq("id", selected_id).execute()
            st.warning(f"Produk ID {selected_id} dihapus dari Cloud.")
            st.rerun()
          except Exception as ex_del:
            st.error(f"Gagal menghapus: {ex_del}")

    # ==========================================
    # SUB-TABEL: RIWAYAT PERUBAHAN HARGA & MODAL (HISTORI)
    # ==========================================
    with st.container(border=True):
      st.markdown(
          "#### 📜 Riwayat Perubahan Harga & Modal (Audit Log):"
          f" **{row_data['nama_produk']}**"
      )

      try:
        res_h = (
            supabase.table("riwayat_harga_produk")
            .select("*")
            .eq("produk_id", selected_id)
            .order("id", desc=True)
            .execute()
        )
        df_histori = (
            pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        )
      except Exception:
        df_histori = pd.DataFrame()

      if df_histori.empty:
        st.info(
            "Belum ada catatan riwayat perubahan. Histori akan tercatat"
            " otomatis saat harga atau modal diubah lalu disimpan."
        )
      else:
        tampil_histori = pd.DataFrame()
        tampil_histori["Tanggal Perubahan"] = df_histori["tanggal_perubahan"]
        tampil_histori["Modal Sebelum"] = df_histori["modal_lama"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        tampil_histori["Modal Baru"] = df_histori["modal_baru"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        tampil_histori["Harga Jual Sebelum"] = df_histori[
            "harga_jual_lama"
        ].apply(lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-")
        tampil_histori["Harga Jual Baru"] = df_histori["harga_jual_baru"].apply(
            lambda x: f"Rp {float(x):,.0f}" if pd.notnull(x) else "-"
        )
        tampil_histori["Rincian Perubahan"] = df_histori["keterangan"]
        tampil_histori["Diubah Oleh"] = df_histori.get("diubah_oleh", "-")

        st.dataframe(
            tampil_histori,
            use_container_width=True,
            hide_index=True,
        )

    # Download CSV
    st.markdown("---")
    csv_data = table_show_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data CSV (Semua Skema Tier)",
        data=csv_data,
        file_name="database_produk_tiers.csv",
        mime="text/csv",
    )

# ==========================================
# TAB 3: KELOLA AKSES TIM (KHUSUS MASTER ADMIN)
# ==========================================
if st.session_state["user_role"] == "admin":
  with tab3:
    st.subheader("👥 Manajemen Hak Akses Tim & Pengguna")
    st.info(
        "💡 Sebagai Master Admin, Anda dapat menyetujui pendaftar baru, mencabut"
        " akses, atau menghapus akun anggota tim."
    )

    try:
      res_users = (
          supabase.table("users_akses")
          .select("*")
          .order("id", desc=False)
          .execute()
      )
      df_users = (
          pd.DataFrame(res_users.data) if res_users.data else pd.DataFrame()
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

        st.dataframe(tampil_users, use_container_width=True, hide_index=True)

      with st.container(border=True):
        st.markdown("##### ⚙️ Aksi Persetujuan & Kontrol Akun")
        list_user_non_admin = df_users[
            df_users["username"] != st.session_state["username"]
        ]

        if list_user_non_admin.empty:
          st.info(
              "Belum ada anggota tim lain yang mendaftar. Anggota baru bisa"
              " mendaftar lewat tab 'Minta Akses (Daftar)' di layar login."
          )
        else:
          user_dict = {
              f"{r['nama_lengkap']} (@{r['username']}) - Status:"
              f" {r['status_akses'].upper()}": r["id"]
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