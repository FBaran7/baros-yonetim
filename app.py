import os
from datetime import date

import pandas as pd
import streamlit as st


# -----------------------------
# Sayfa ayarları
# -----------------------------
st.set_page_config(
    page_title="Yönetim, Stok ve Karlılık Kontrol Sistemi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# Dosya yolları
# -----------------------------
SATISLAR_DOSYA = "satislar.csv"
GIDERLER_DOSYA = "giderler.csv"


# -----------------------------
# Yardımcı fonksiyonlar
# -----------------------------
def format_tl(amount: float) -> str:
    """Sayıyı TL formatında gösterir."""
    return f"{amount:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def summary_card(title: str, value: str, icon: str, bg_color: str = "#ffffff"):
    """Premium özet kartı."""
    st.markdown(
        f"""
        <div class="ozet-kart" style="background-color: {bg_color};">
            <div class="ozet-ikon">{icon}</div>
            <div class="ozet-baslik">{title}</div>
            <div class="ozet-deger">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def csv_dosyalarini_hazirla():
    """CSV dosyaları yoksa oluşturur."""
    if not os.path.exists(SATISLAR_DOSYA):
        pd.DataFrame(
            columns=["Tarih", "Müşteri", "Sipariş No", "Tutar"]
        ).to_csv(SATISLAR_DOSYA, index=False, encoding="utf-8-sig")

    if not os.path.exists(GIDERLER_DOSYA):
        pd.DataFrame(
            columns=["Tarih", "Gider Kalemi", "Tutar"]
        ).to_csv(GIDERLER_DOSYA, index=False, encoding="utf-8-sig")


def satislari_oku() -> pd.DataFrame:
    """Satışlar CSV dosyasını okur."""
    df = pd.read_csv(SATISLAR_DOSYA, encoding="utf-8-sig")

    if df.empty:
        df = pd.DataFrame(columns=["Tarih", "Müşteri", "Sipariş No", "Tutar"])

    if "Tarih" in df.columns:
        df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", dayfirst=True)

    if "Tutar" in df.columns:
        df["Tutar"] = pd.to_numeric(df["Tutar"], errors="coerce").fillna(0)

    return df


def giderleri_oku() -> pd.DataFrame:
    """Giderler CSV dosyasını okur."""
    df = pd.read_csv(GIDERLER_DOSYA, encoding="utf-8-sig")

    if df.empty:
        df = pd.DataFrame(columns=["Tarih", "Gider Kalemi", "Tutar"])

    if "Tarih" in df.columns:
        df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", dayfirst=True)

    if "Tutar" in df.columns:
        df["Tutar"] = pd.to_numeric(df["Tutar"], errors="coerce").fillna(0)

    return df


def bu_ay_toplam_hesapla(df: pd.DataFrame) -> float:
    """Verilen DataFrame için bu ayın toplam tutarını hesaplar."""
    if df.empty or "Tarih" not in df.columns or "Tutar" not in df.columns:
        return 0.0

    bugun = pd.Timestamp.today()
    filtre = (
        (df["Tarih"].dt.month == bugun.month) &
        (df["Tarih"].dt.year == bugun.year)
    )
    return float(df.loc[filtre, "Tutar"].sum())


def tablo_gosterime_hazirla(df: pd.DataFrame, tutar_kolonu: str) -> pd.DataFrame:
    """Tabloyu ekranda gösterilecek hale getirir."""
    df_gosterim = df.copy()

    if "Tarih" in df_gosterim.columns:
        df_gosterim["Tarih"] = pd.to_datetime(
            df_gosterim["Tarih"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    if tutar_kolonu in df_gosterim.columns:
        df_gosterim[tutar_kolonu] = df_gosterim[tutar_kolonu].apply(format_tl)

    return df_gosterim


# -----------------------------
# CSV dosyalarını hazırla
# -----------------------------
csv_dosyalarini_hazirla()


# -----------------------------
# Sabit demo veriler
# -----------------------------
toplam_stok_maliyeti = 2_490_000
toplam_musteri_alacagi = 1_180_000
toplam_tedarikci_borcu = 790_000

yaklasan_odemeler_df = pd.DataFrame(
    {
        "Tedarikçi": ["Aydin Kumaş", "Moda Etiket", "Delta Aksesuar", "Mert Kargo"],
        "Vade Tarihi": ["12.04.2026", "15.04.2026", "18.04.2026", "22.04.2026"],
        "Tutar": [
            format_tl(120_000),
            format_tl(75_000),
            format_tl(48_000),
            format_tl(32_000),
        ],
    }
)

stok_gruplari_df = pd.DataFrame(
    {
        "Ürün Grubu": ["Gömlek", "Mont", "Tişört", "Sweatshirt", "Pantolon"],
        "Stok Değeri": [
            format_tl(1_250_000),
            format_tl(830_000),
            format_tl(410_000),
            format_tl(290_000),
            format_tl(210_000),
        ],
    }
)

stok_detay_df = pd.DataFrame(
    {
        "Ürün Kodu": ["BRS-GMLK-001", "BRS-MNT-004", "BRS-TSRT-012", "BRS-SWT-006"],
        "Ürün Adı": ["Slim Fit Gömlek", "Kapitone Mont", "Basic Tişört", "Kapüşonlu Sweat"],
        "Kategori": ["Gömlek", "Mont", "Tişört", "Sweatshirt"],
        "Stok Adedi": [320, 110, 540, 180],
        "Birim Maliyet": [
            format_tl(850),
            format_tl(2_300),
            format_tl(280),
            format_tl(650)
        ],
    }
)

cari_df = pd.DataFrame(
    {
        "Cari Adı": ["Yıldız Butik", "Trend Erkek", "Asil Giyim", "Akdeniz Moda"],
        "Tür": ["Müşteri", "Müşteri", "Tedarikçi", "Tedarikçi"],
        "Bakiye": [
            format_tl(320_000),
            format_tl(210_000),
            format_tl(185_000),
            format_tl(96_000),
        ],
        "Durum": ["Alacak", "Alacak", "Borç", "Borç"],
    }
)


# -----------------------------
# Dinamik veriler
# -----------------------------
satislar_df = satislari_oku()
giderler_df = giderleri_oku()

bu_ay_satis = bu_ay_toplam_hesapla(satislar_df)
bu_ay_toplam_gider = bu_ay_toplam_hesapla(giderler_df)
bu_ay_net_kar = bu_ay_satis - bu_ay_toplam_gider

satislar_gosterim_df = tablo_gosterime_hazirla(satislar_df, "Tutar")
giderler_gosterim_df = tablo_gosterime_hazirla(giderler_df, "Tutar")


# -----------------------------
# Premium stil
# -----------------------------
st.markdown(
    """
    <style>
        /* Genel arka plan */
        .stApp {
            background: #f4f5f7;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        /* Sadece ana menü ve footer gizle */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Sidebar toggle butonu görünür kalsın */
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f7f8fa 100%);
            border-right: 1px solid rgba(15, 23, 42, 0.06);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }

        /* Yazılar */
        h1, h2, h3 {
            color: #111827;
            letter-spacing: -0.02em;
        }

        p, label, div {
            color: #1f2937;
        }

        /* Kartlar */
        .ozet-kart {
            padding: 22px;
            border-radius: 20px;
            border: 1px solid rgba(15, 23, 42, 0.06);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
            min-height: 140px;
            transition: all 0.2s ease;
        }

        .ozet-kart:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.10);
        }

        .ozet-ikon {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .ozet-baslik {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .ozet-deger {
            font-size: 30px;
            font-weight: 800;
            color: #111827;
            line-height: 1.1;
        }

        /* Metric kutuları */
        [data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 18px;
            padding: 18px 18px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        [data-testid="metric-container"] label {
            color: #6b7280 !important;
            font-weight: 600;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #111827;
            font-weight: 800;
        }

        /* Dataframe / tablo */
        div[data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        /* Form alanları */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div,
        .stDateInput > div > div {
            border-radius: 14px !important;
            border: 1px solid rgba(15, 23, 42, 0.08) !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        /* Butonlar */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            width: 100%;
            border-radius: 14px;
            border: none;
            background: linear-gradient(135deg, #111827 0%, #374151 100%);
            color: #ffffff;
            font-weight: 700;
            padding: 0.72rem 1rem;
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.18);
            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 28px rgba(17, 24, 39, 0.24);
            background: linear-gradient(135deg, #0f172a 0%, #1f2937 100%);
        }

        .stButton > button:focus,
        [data-testid="stFormSubmitButton"] > button:focus {
            outline: none;
            box-shadow: 0 0 0 0.2rem rgba(55, 65, 81, 0.18);
        }

        /* Radio menü */
        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.3rem;
        }

        [data-testid="stSidebar"] label[data-baseweb="radio"] {
            background: #ffffff;
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 14px;
            padding: 8px 10px;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.03);
        }

        /* Info / success mesajları */
        [data-testid="stAlert"] {
            border-radius: 16px;
            border: 1px solid rgba(15, 23, 42, 0.06);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar
# -----------------------------
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.title("📂 Menü")
sayfa = st.sidebar.radio(
    "Sayfa Seçin",
    [
        "Ana Panel",
        "Stok Değerleme",
        "Cari",
        "Satışlar",
        "Giderler",
        "Veri Girişi",
        "Maliyet Simülatörü"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Baros Yönetim Sistemi")
st.sidebar.caption("Premium demo arayüz")


# -----------------------------
# Sayfalar
# -----------------------------
if sayfa == "Ana Panel":
    st.title("📊 Ana Panel")
    st.caption("Yönetim, Stok ve Karlılık Kontrol Sistemi - Dinamik Görünüm")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        summary_card(
            "Toplam Stok Maliyeti",
            format_tl(toplam_stok_maliyeti),
            "📦"
        )

    with col2:
        summary_card(
            "Toplam Müşteri Alacağı",
            format_tl(toplam_musteri_alacagi),
            "💰"
        )

    with col3:
        summary_card(
            "Toplam Tedarikçi Borcu",
            format_tl(toplam_tedarikci_borcu),
            "🏷️"
        )

    with col4:
        summary_card(
            "Bu Ay Net Kâr",
            format_tl(bu_ay_net_kar),
            "📈"
        )

    st.markdown("###")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Bu Ay Satış", format_tl(bu_ay_satis))
    with m2:
        st.metric("Bu Ay Toplam Gider", format_tl(bu_ay_toplam_gider))
    with m3:
        st.metric("Bu Ay Net Kâr", format_tl(bu_ay_net_kar))

    st.markdown("###")

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Yaklaşan Ödemeler")
        st.dataframe(yaklasan_odemeler_df, use_container_width=True, hide_index=True)

    with right_col:
        st.subheader("En Çok Para Bağlanan Stok Grupları")
        st.dataframe(stok_gruplari_df, use_container_width=True, hide_index=True)

elif sayfa == "Stok Değerleme":
    st.title("📦 Stok Değerleme")
    st.caption("Sahte verilerle hazırlanmış örnek stok ekranı")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Toplam Stok Maliyeti", format_tl(toplam_stok_maliyeti))
    with c2:
        st.metric("Toplam Satış Değeri", format_tl(4_180_000))
    with c3:
        st.metric("Toplam Ürün Adedi", "1.150")

    st.markdown("### Stok Detayları")
    st.dataframe(stok_detay_df, use_container_width=True, hide_index=True)

elif sayfa == "Cari":
    st.title("💳 Cari")
    st.caption("Müşteri ve tedarikçi bakiyeleri için örnek görünüm")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Toplam Müşteri Alacağı", format_tl(toplam_musteri_alacagi))
    with c2:
        st.metric("Toplam Tedarikçi Borcu", format_tl(toplam_tedarikci_borcu))

    st.markdown("### Cari Listesi")
    st.dataframe(cari_df, use_container_width=True, hide_index=True)

elif sayfa == "Satışlar":
    st.title("🧾 Satışlar")
    st.caption("CSV dosyasından okunan satış hareketleri")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Bu Ay Satış", format_tl(bu_ay_satis))
    with c2:
        st.metric("Toplam Sipariş", str(len(satislar_df)))
    with c3:
        ortalama_siparis = satislar_df["Tutar"].mean() if not satislar_df.empty else 0
        st.metric("Ortalama Sipariş", format_tl(ortalama_siparis))

    st.markdown("### Son Satışlar")
    st.dataframe(satislar_gosterim_df, use_container_width=True, hide_index=True)

elif sayfa == "Giderler":
    st.title("💸 Giderler")
    st.caption("CSV dosyasından okunan gider hareketleri")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Bu Ay Toplam Gider", format_tl(bu_ay_toplam_gider))
    with c2:
        en_yuksek_gider = "-"
        if not giderler_df.empty:
            idx = giderler_df["Tutar"].idxmax()
            en_yuksek_gider = giderler_df.loc[idx, "Gider Kalemi"]
        st.metric("En Yüksek Gider Kalemi", en_yuksek_gider)

    st.markdown("### Gider Listesi")
    st.dataframe(giderler_gosterim_df, use_container_width=True, hide_index=True)

elif sayfa == "Veri Girişi":
    st.title("📝 Veri Girişi")
    st.caption("Yeni satış ve gider kayıtlarını CSV dosyalarına ekleyin")

    sol, sag = st.columns(2)

    with sol:
        st.subheader("Yeni Satış Ekle")
        with st.form("yeni_satis_formu", clear_on_submit=True):
            satis_tarih = st.date_input("Tarih", value=date.today(), key="satis_tarih")
            satis_musteri = st.text_input("Müşteri", key="satis_musteri")
            satis_siparis_no = st.text_input("Sipariş No", key="satis_siparis_no")
            satis_tutar = st.number_input(
                "Tutar",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="satis_tutar"
            )

            satis_submit = st.form_submit_button("Satışı Kaydet")

            if satis_submit:
                if not satis_musteri.strip() or not satis_siparis_no.strip():
                    st.error("Lütfen tüm satış alanlarını doldurun.")
                else:
                    yeni_satis = pd.DataFrame(
                        [{
                            "Tarih": pd.to_datetime(satis_tarih).strftime("%d.%m.%Y"),
                            "Müşteri": satis_musteri.strip(),
                            "Sipariş No": satis_siparis_no.strip(),
                            "Tutar": satis_tutar
                        }]
                    )
                    yeni_satis.to_csv(
                        SATISLAR_DOSYA,
                        mode="a",
                        header=False,
                        index=False,
                        encoding="utf-8-sig"
                    )
                    st.success("Yeni satış başarıyla kaydedildi.")

    with sag:
        st.subheader("Yeni Gider Ekle")
        with st.form("yeni_gider_formu", clear_on_submit=True):
            gider_tarih = st.date_input("Tarih", value=date.today(), key="gider_tarih")
            gider_kalemi = st.text_input("Gider Kalemi", key="gider_kalemi")
            gider_tutar = st.number_input(
                "Tutar",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="gider_tutar"
            )

            gider_submit = st.form_submit_button("Gideri Kaydet")

            if gider_submit:
                if not gider_kalemi.strip():
                    st.error("Lütfen gider kalemini girin.")
                else:
                    yeni_gider = pd.DataFrame(
                        [{
                            "Tarih": pd.to_datetime(gider_tarih).strftime("%d.%m.%Y"),
                            "Gider Kalemi": gider_kalemi.strip(),
                            "Tutar": gider_tutar
                        }]
                    )
                    yeni_gider.to_csv(
                        GIDERLER_DOSYA,
                        mode="a",
                        header=False,
                        index=False,
                        encoding="utf-8-sig"
                    )
                    st.success("Yeni gider başarıyla kaydedildi.")

    st.markdown("###")
    st.info("Not: Kayıt ekledikten sonra diğer sayfalardaki metrikler ve tablolar güncel verilerle çalışır.")

elif sayfa == "Maliyet Simülatörü":
    st.title("🧮 Maliyet Simülatörü")
    st.caption("Tekstil üretimi için maliyet, toptan satış ve Trendyol satış fiyatı simülasyonu")

    col1, col2, col3 = st.columns(3)

    with col1:
        kumas_metre_fiyati = st.number_input(
            "Kumaş Metre Fiyatı (TL)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            value=150.0
        )
        urun_basina_kumas = st.number_input(
            "Ürün Başına Harcanan Kumaş (Metre)",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            value=1.8
        )

    with col2:
        fason_dikim_maliyeti = st.number_input(
            "Fason Dikim Maliyeti (TL)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            value=90.0
        )
        aksesuar_ve_diger = st.number_input(
            "Aksesuar ve Diğer Giderler (Fermuar, etiket vb. TL)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            value=35.0
        )

    with col3:
        hedef_toptan_kar_marji = st.number_input(
            "Hedef Toptan Kâr Marjı (%)",
            min_value=0.0,
            max_value=1000.0,
            step=1.0,
            format="%.2f",
            value=35.0
        )
        trendyol_komisyon_orani = st.number_input(
            "Trendyol Komisyon Oranı (%)",
            min_value=0.0,
            max_value=99.0,
            step=0.1,
            format="%.2f",
            value=21.5
        )

    net_uretim_maliyeti = (
        (kumas_metre_fiyati * urun_basina_kumas)
        + fason_dikim_maliyeti
        + aksesuar_ve_diger
    )

    toptan_satis_fiyati = net_uretim_maliyeti + (
        net_uretim_maliyeti * hedef_toptan_kar_marji / 100
    )

    if trendyol_komisyon_orani >= 100:
        trendyol_satis_fiyati = 0.0
    else:
        trendyol_satis_fiyati = toptan_satis_fiyati / (
            1 - trendyol_komisyon_orani / 100
        )

    st.markdown("###")

    r1, r2, r3 = st.columns(3)

    with r1:
        summary_card(
            "Net Üretim Maliyeti",
            format_tl(net_uretim_maliyeti),
            "🏭",
            "#eef6ff"
        )

    with r2:
        summary_card(
            "Toptan Satış Fiyatı",
            format_tl(toptan_satis_fiyati),
            "🏷️",
            "#eefbf3"
        )

    with r3:
        summary_card(
            "Trendyol (Perakende) Satış Fiyatı",
            format_tl(trendyol_satis_fiyati),
            "🛒",
            "#fff6ea"
        )

    st.markdown("###")
    st.subheader("Hesaplama Özeti")

    ozet_df = pd.DataFrame(
        {
            "Kalem": [
                "Kumaş Toplamı",
                "Fason Dikim",
                "Aksesuar ve Diğer",
                "Net Üretim Maliyeti",
                "Toptan Kâr Marjı",
                "Trendyol Komisyonu"
            ],
            "Değer": [
                format_tl(kumas_metre_fiyati * urun_basina_kumas),
                format_tl(fason_dikim_maliyeti),
                format_tl(aksesuar_ve_diger),
                format_tl(net_uretim_maliyeti),
                f"%{hedef_toptan_kar_marji:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"%{trendyol_komisyon_orani:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ]
        }
    )

    st.dataframe(ozet_df, use_container_width=True, hide_index=True)