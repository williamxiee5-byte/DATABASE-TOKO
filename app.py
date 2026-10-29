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


# -------------------- Header --------------------
st.markdown('<div class="main-title">🛒 GM Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Kalkulator HPP, laba, dan margin produk</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Menu")
    page = st.radio("Pilih halaman", ["Ringkasan & Daftar Produk", "Tambah Produk", "Edit / Hapus Produk"])
    st.divider()
    st.caption("Data tersimpan di Supabase.")
    if APP_PASSWORD and st.button("Keluar"):
        st.session_state["authenticated"] = False
        st.rerun()


# -------------------- Load data --------------------
try:
    products = fetch_products()
except Exception as exc:
    st.error("Tidak bisa membaca tabel Supabase.")
    st.code(str(exc))
    st.markdown(
        "Pastikan tabel `produk`, kolom, dan Storage bucket sudah dibuat sesuai file `supabase_setup.sql`."
    )
    st.stop()

products_by_id = {str(p.get("id")): p for p in products}


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
            harga_jual = st.number_input(
                "Harga jual (Rp)", min_value=0, step=1000,
                value=int(as_float(initial.get("harga_jual"))),
            )
        with c3:
            foto = st.file_uploader(
                "Foto produk (opsional)", type=["png", "jpg", "jpeg", "webp"],
                key=f"{prefix}_photo",
            )
            current_photo = str(initial.get("foto_url", "") or "")
            if current_photo:
                st.caption("Foto saat ini tersimpan.")

        st.subheader("Komponen HPP per unit")
        a, b, c = st.columns(3)
        with a:
            hpp_barang = st.number_input(
                "Harga beli / bahan (Rp)", min_value=0, step=500,
                value=int(as_float(initial.get("hpp_barang"))),
            )
            biaya_kemasan = st.number_input(
                "Biaya kemasan (Rp)", min_value=0, step=100,
                value=int(as_float(initial.get("biaya_kemasan"))),
            )
        with b:
            biaya_tenaga_kerja = st.number_input(
                "Biaya tenaga kerja (Rp)", min_value=0, step=100,
                value=int(as_float(initial.get("biaya_tenaga_kerja"))),
            )
            biaya_lain = st.number_input(
                "Biaya lain (Rp)", min_value=0, step=100,
                value=int(as_float(initial.get("biaya_lain"))),
            )
        with c:
            fee_marketplace_pct = st.number_input(
                "Fee marketplace (%)", min_value=0.0, max_value=100.0, step=0.5,
                value=as_float(initial.get("fee_marketplace_pct", 0)),
            )
            affiliate_pct = st.number_input(
                "Affiliate (%)", min_value=0.0, max_value=100.0, step=0.5,
                value=as_float(initial.get("affiliate_pct", 0)),
            )
        biaya_iklan_per_unit = st.number_input(
            "Biaya iklan per unit terjual (Rp)", min_value=0, step=100,
            value=int(as_float(initial.get("biaya_iklan_per_unit"))),
            help="Isi biaya iklan rata-rata per unit. Jangan isi ROAS di kolom ini.",
        )

        draft = {
            "harga_jual": harga_jual,
            "hpp_barang": hpp_barang,
            "biaya_kemasan": biaya_kemasan,
            "biaya_tenaga_kerja": biaya_tenaga_kerja,
            "biaya_lain": biaya_lain,
            "fee_marketplace_pct": fee_marketplace_pct,
            "affiliate_pct": affiliate_pct,
            "biaya_iklan_per_unit": biaya_iklan_per_unit,
        }
        result = calculate(draft)
        st.divider()
        st.subheader("Simulasi hasil")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total HPP", rupiah(result["hpp_total"]))
        m2.metric("Total biaya termasuk fee/iklan", rupiah(result["total_biaya"]))
        m3.metric("Laba bersih per unit", rupiah(result["laba_bersih"]))
        m4.metric("Margin bersih", f'{result["margin_pct"]:.2f}%')

        submitted = st.form_submit_button(
            "Simpan Produk" if prefix == "add" else "Simpan Perubahan",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not nama.strip():
            st.error("Nama produk wajib diisi.")
            return
        payload = {
            "nama": nama.strip(),
            "sku": sku.strip(),
            "variasi": variasi.strip(),
            "harga_jual": int(harga_jual),
            "hpp_barang": int(hpp_barang),
            "biaya_kemasan": int(biaya_kemasan),
            "biaya_tenaga_kerja": int(biaya_tenaga_kerja),
            "biaya_lain": int(biaya_lain),
            "fee_marketplace_pct": float(fee_marketplace_pct),
            "affiliate_pct": float(affiliate_pct),
            "biaya_iklan_per_unit": int(biaya_iklan_per_unit),
            "foto_url": current_photo,
        }
        try:
            if foto is not None:
                uploaded_url = upload_photo(foto, sku.strip() or nama.strip())
                if uploaded_url:
                    payload["foto_url"] = uploaded_url
            save_product(payload, initial.get("id"))
            st.success("Produk berhasil disimpan ke Supabase.")
            st.rerun()
        except Exception as exc:
            st.error("Gagal menyimpan produk. Periksa konfigurasi tabel, key, dan Storage.")
            st.code(str(exc))


if page == "Ringkasan & Daftar Produk":
    if not products:
        st.info("Belum ada produk. Buka menu **Tambah Produk** untuk mulai.")
    else:
        calculated = []
        for p in products: