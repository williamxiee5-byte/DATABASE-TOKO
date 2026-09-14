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
# 2. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Kalkulator HPP & Database Cloud",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ Manajemen HPP, Margin & Database Cloud (Online)")
tab1, tab2 = st.tabs(
    ["🧮 Tab 1: Kalkulator HPP & ROAS", "📦 Tab 2: Data Barang (Cloud)"]
)

# ==========================================
# TAB 1: KALKULATOR
# ==========================================
with tab1:
    st.subheader("Simulasi & Kalkulasi Produk")
    col_input, col_result = st.columns([1.1, 1.2], gap="large")

    with col_input:
        st.markdown("##### 📌 Informasi Produk & Modal")
        nama_produk = st.text_input(
            "Nama Produk", placeholder="Contoh: Kemeja Linen Pria"
        )

        c1, c2 = st.columns(2)
        min_order = c1.number_input(
            "Minimum Order (Qty)", min_value=1, value=2, step=1, key="t1_mo"
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
            f"🔒 Total Modal Produk ({min_order} Pcs) (Locked)",
            value=total_modal,
            disabled=True,
            format="%.0f",
        )

        st.markdown("##### 🏷️ Penetapan Harga Jual")
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
            f"🔒 Total Harga Jual Paket ({min_order} Pcs) (Locked)",
            value=harga_jual_total,
            disabled=True,
            format="%.0f",
        )

        st.markdown("##### ⚙️ Biaya Transaksi & Operasional")
        c3, c4 = st.columns(2)
        biaya_proses = 1250.0
        c3.number_input(
            "🔒 Biaya Pemrosesan (Locked)",
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
        st.markdown("##### 📈 Hasil Perhitungan & Rincian Paket Order")

        m1, m2, m3 = st.columns(3)
        m1.metric(
            f"Laba Bersih ({min_order} Pcs)",
            f"Rp {laba_bersih_total:,.0f}",
            delta=f"Rp {laba_bersih_unit:,.0f} / unit",
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

        st.markdown(
            f"**Rincian Beban Biaya & Omset (Paket {min_order} Pcs):**"
        )
        rincian_df = pd.DataFrame(
            {
                "Komponen Biaya": [
                    f"1. Modal Pokok Produk ({min_order} pcs @ Rp {modal_unit:,.0f})",
                    "2. Biaya Pemrosesan Pesanan (Fixed)",
                    "3. Biaya Packing",
                    f"4. Biaya AMS ({biaya_ams_persen}%)",
                    f"5. Biaya Marketplace ({biaya_mp_persen}%)",
                    "TOTAL HPP & BEBAN OPERASIONAL",
                    f"TOTAL HARGA JUAL / OMSET ({min_order} pcs)",
                ],
                "Nominal (Rp)": [
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
                f"💡 **Penjelasan BEP ROAS ({bep_roas:.2f}x):** Setiap budget iklan **Rp 100.000**, "
                f"omzet minimal **Rp {bep_roas * 100000:,.0f}** agar tidak rugi."
            )
        else:
            st.error(
                "⚠️ Beban melebihi harga jual (Margin Minus). Naikkan harga jual atau pangkas biaya!"
            )

        st.markdown("---")
        if st.button(
            "💾 Simpan ke Database Cloud",
            type="primary",
            use_container_width=True,
        ):
            if not nama_produk.strip():
                st.warning("⚠️ Masukkan nama produk terlebih dahulu!")
            else:
                insert_payload = {
                    "tanggal_input": datetime.now().strftime("%Y-%m-%d %H:%M"),
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
                    supabase.table("produk").insert(insert_payload).execute()
                    st.success(
                        f"✅ Produk **'{nama_produk}'** berhasil tersimpan di Cloud Supabase!"
                    )
                    st.rerun()
                except Exception as ex:
                    st.error(f"Gagal menyimpan data ke cloud: {ex}")

# ==========================================
# TAB 2: DATA BARANG (CLOUD & CARD PREVIEW)
# ==========================================
with tab2:
    st.subheader("📦 Database Barang di Cloud & Detail Card")

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
        st.info(
            "Belum ada data barang di Cloud. Silakan input produk dan klik 'Simpan ke Database Cloud' di Tab 1."
        )
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

        st.markdown("**Klik salah satu baris pada tabel untuk membuka Card:**")
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
                "Atau Pilih Produk dari Menu:",
                list(options_dict.keys()),
                index=0,
            )
            selected_id = options_dict[pilihan]

        row_data = df_raw[df_raw["id"] == selected_id].iloc[0]

        st.markdown("---")
        st.markdown(
            f"### 🎴 Card Produk: **{row_data['nama_produk']}** (ID: {selected_id})"
        )

        card_col_img, card_col_form = st.columns([1, 2], gap="large")

        with card_col_img:
            st.markdown("##### 🖼️ Foto Produk (Cloud Storage)")
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
                st.info("📷 Belum ada foto di Cloud untuk produk ini.")

            uploaded_file = st.file_uploader(
                "Unggah / Ganti Foto ke Cloud",
                type=["png", "jpg", "jpeg"],
                key=f"uploader_{selected_id}",
            )

        with card_col_form:
            st.markdown("##### ✏️ Parameter & Harga Aktif")

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
            e_laba_unit = e_laba_total / e_min_order if e_min_order > 0 else 0.0
            e_margin_persen = (
                (e_laba_total / e_total_omset * 100) if e_total_omset > 0 else 0
            )
            e_bep_roas = (
                e_total_omset / e_laba_total if e_laba_total > 0 else 0.0
            )

            st.markdown("**Performa Saat Ini:**")
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
                        f"✅ Data produk **'{e_nama}'** berhasil diperbarui di Cloud!"
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
                        f"Produk ID {selected_id} berhasil dihapus dari Cloud."
                    )
                    st.rerun()
                except Exception as ex_del:
                    st.error(f"Gagal menghapus: {ex_del}")

        # Sub-Tabel Variasi Modal Cloud
        st.markdown("---")
        st.markdown(
            f"#### 📑 Sub-Tabel Variasi & Perubahan Modal ({row_data['nama_produk']})"
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

        col_tabel_modal, col_form_modal = st.columns([1.3, 1], gap="medium")

        with col_tabel_modal:
            if df_modal.empty:
                st.info(
                    "Belum ada variasi modal tambahan di Cloud. Tambahkan catatan perubahan modal pada formulir di sebelah kanan."
                )
            else:
                tampil_modal = pd.DataFrame()
                tampil_modal["ID"] = df_modal["id"]
                tampil_modal["Tanggal"] = df_modal["tanggal_update"]
                tampil_modal["Nama / Label Modal (Custom)"] = df_modal[
                    "nama_keterangan"
                ]
                tampil_modal["Nominal Modal (Rp)"] = df_modal[
                    "nominal_modal"
                ].apply(lambda x: f"Rp {float(x):,.0f}")

                st.dataframe(
                    tampil_modal, use_container_width=True, hide_index=True
                )

                c_sel_m, c_btn_m, c_btn_del = st.columns([1.5, 1, 0.8])
                pilihan_modal_dict = {
                    f"{r['nama_keterangan']} (Rp {float(r['nominal_modal']):,.0f})": (
                        r["id"],
                        r["nominal_modal"],
                    )
                    for _, r in df_modal.iterrows()
                }

                pilih_entry = c_sel_m.selectbox(
                    "Pilih Modal untuk diterapkan/dihapus:",
                    list(pilihan_modal_dict.keys()),
                    key=f"sel_m_{selected_id}",
                )
                id_modal_terpilih, modal_nilai_terpilih = pilihan_modal_dict[
                    pilih_entry
                ]

                if c_btn_m.button(
                    "⚡ Terapkan Jadi Modal Utama",
                    use_container_width=True,
                    key=f"btn_apply_{selected_id}",
                ):
                    try:
                        supabase.table("produk").update(
                            {"modal_unit": float(modal_nilai_terpilih)}
                        ).eq("id", selected_id).execute()
                        st.success(
                            f"Modal utama diubah menjadi Rp {float(modal_nilai_terpilih):,.0f}!"
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
                        st.warning("Data modal kustom dihapus dari Cloud.")
                        st.rerun()
                    except Exception as ex_del_m:
                        st.error(f"Gagal menghapus modal: {ex_del_m}")

        with col_form_modal:
            st.markdown("**➕ Tambah Catatan Modal Kustom Baru**")
            label_modal_baru = st.text_input(
                "Nama Label / Kolom Kustom",
                placeholder="Contoh: Modal Supplier B / Modal Batch 2",
                key=f"lbl_m_{selected_id}",
            )
            nominal_modal_baru = st.number_input(
                "Nominal Modal Baru (Rp)",
                min_value=0.0,
                value=float(row_data["modal_unit"]),
                step=100.0,
                key=f"nom_m_{selected_id}",
            )
            terapkan_langsung = st.checkbox(
                "Langsung terapkan sebagai modal aktif produk?",
                value=False,
                key=f"chk_apply_{selected_id}",
            )

            if st.button(
                "Simpan Kolom Modal Baru ke Cloud",
                type="primary",
                use_container_width=True,
                key=f"btn_add_modal_{selected_id}",
            ):
                if not label_modal_baru.strip():
                    st.warning("⚠️ Masukkan nama label atau keterangan modal!")
                else:
                    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
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
                        st.success(
                            f"✅ Catatan modal **'{label_modal_baru}'** tersimpan di Cloud!"
                        )
                        st.rerun()
                    except Exception as ex_in_m:
                        st.error(f"Gagal menambah modal: {ex_in_m}")

        st.markdown("---")
        csv_data = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Seluruh Data Cloud (CSV)",
            data=csv_data,
            file_name="database_produk_cloud.csv",
            mime="text/csv",
        )