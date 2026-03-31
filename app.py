import os
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# Kimlik doğrulama / roller
# -----------------------------
GECERLI_KULLANICILAR = {
    "patron": {"password": "baros2026", "role": "admin"},
    "depo": {"password": "depo123", "role": "staff"},
}

ADMIN_SAYFALARI = [
    "Ana Panel",
    "Stok Değerleme",
    "Cari",
    "Satışlar",
    "Giderler",
    "Veri Girişi",
    "Maliyet Simülatörü",
]

STAFF_SAYFALARI = [
    "Veri Girişi",
    "Stok Değerleme",
]

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

if "role" not in st.session_state:
    st.session_state["role"] = ""


def giris_ekrani_goster():
    """Sadece giriş ekranını gösterir."""
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #f4f5f7 0%, #eef2f7 100%);
            }

            #MainMenu, footer, header,
            section[data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none !important;
            }

            .block-container {
                padding-top: 4rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }

            .giris-karti {
                background: rgba(255, 255, 255, 0.96);
                padding: 34px 28px 28px 28px;
                border-radius: 28px;
                border: none;
                box-shadow: 0 24px 64px rgba(15, 23, 42, 0.10);
                backdrop-filter: blur(10px);
            }

            .giris-baslik {
                font-size: 32px;
                font-weight: 800;
                color: #111827;
                text-align: center;
                margin-bottom: 8px;
                letter-spacing: -0.02em;
            }

            .giris-aciklama {
                font-size: 15px;
                color: #6b7280;
                text-align: center;
                margin-bottom: 24px;
            }

            /* Mobil dark mode / tüm inputlar için kesin renk düzeltmesi */
            input, textarea, select {
                color: #111827 !important;
                background-color: #ffffff !important;
                -webkit-text-fill-color: #111827 !important;
                caret-color: #111827 !important;
            }

            input::placeholder,
            textarea::placeholder,
            select::placeholder {
                color: #6b7280 !important;
                -webkit-text-fill-color: #6b7280 !important;
                opacity: 1 !important;
            }

            div[data-baseweb="input"] > div,
            div[data-baseweb="textarea"] > div,
            div[data-baseweb="select"] > div,
            .stDateInput > div > div {
                border-radius: 16px !important;
                border: 1px solid rgba(15, 23, 42, 0.08) !important;
                background: #ffffff !important;
                box-shadow: none !important;
            }

            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea,
            div[data-baseweb="select"] input,
            .stDateInput input {
                color: #111827 !important;
                background-color: #ffffff !important;
                -webkit-text-fill-color: #111827 !important;
                caret-color: #111827 !important;
            }

            div[data-baseweb="input"] input::placeholder,
            div[data-baseweb="textarea"] textarea::placeholder,
            div[data-baseweb="select"] input::placeholder,
            .stDateInput input::placeholder {
                color: #6b7280 !important;
                -webkit-text-fill-color: #6b7280 !important;
                opacity: 1 !important;
            }

            [data-testid="stFormSubmitButton"] > button {
                width: 100%;
                border-radius: 16px;
                border: none;
                background: linear-gradient(135deg, #111827 0%, #374151 100%);
                color: #ffffff;
                font-weight: 700;
                padding: 0.82rem 1rem;
                box-shadow: 0 10px 22px rgba(17, 24, 39, 0.18);
                transition: all 0.2s ease;
            }

            [data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 14px 28px rgba(17, 24, 39, 0.24);
                background: linear-gradient(135deg, #0f172a 0%, #1f2937 100%);
            }

            .giris-alti-not {
                margin-top: 20px;
                text-align: center;
                color: #9ca3af;
                font-size: 13px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    bos1, orta, bos2 = st.columns([1.2, 1, 1.2])

    with orta:
        st.markdown('<div class="giris-karti">', unsafe_allow_html=True)
        st.markdown('<div class="giris-baslik">Giriş Yap</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="giris-aciklama">Yönetim, Stok ve Karlılık Kontrol Sistemi</div>',
            unsafe_allow_html=True
        )

        with st.form("giris_formu", clear_on_submit=False):
            kullanici_adi = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            giris_buton = st.form_submit_button("Giriş Yap")

            if giris_buton:
                kullanici = GECERLI_KULLANICILAR.get(kullanici_adi)

                if kullanici and kullanici["password"] == sifre:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = kullanici_adi
                    st.session_state["role"] = kullanici["role"]
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

        st.markdown(
            '<div class="giris-alti-not">Yetkisiz erişim engellenmiştir.</div>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state["logged_in"]:
    giris_ekrani_goster()
    st.stop()


# -----------------------------
# Dosya yolları
# -----------------------------
SATISLAR_DOSYA = "satislar.csv"
GIDERLER_DOSYA = "giderler.csv"
STOK_DOSYA = "stok.csv"


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

    if not os.path.exists(STOK_DOSYA):
        pd.DataFrame(
            columns=["Ürün Kodu", "Ürün Adı", "Kategori", "Stok Adedi", "Birim Maliyet"]
        ).to_csv(STOK_DOSYA, index=False, encoding="utf-8-sig")


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


def stok_oku() -> pd.DataFrame:
    """Stok CSV dosyasını okur."""
    df = pd.read_csv(STOK_DOSYA, encoding="utf-8-sig")

    if df.empty:
        df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Kategori", "Stok Adedi", "Birim Maliyet"])

    if "Stok Adedi" in df.columns:
        df["Stok Adedi"] = pd.to_numeric(df["Stok Adedi"], errors="coerce").fillna(0)

    if "Birim Maliyet" in df.columns:
        df["Birim Maliyet"] = pd.to_numeric(df["Birim Maliyet"], errors="coerce").fillna(0)

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


def stok_tablo_gosterime_hazirla(df: pd.DataFrame) -> pd.DataFrame:
    """Stok tablosunu ekranda gösterilecek hale getirir."""
    if df.empty:
        return pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Kategori", "Stok Adedi", "Birim Maliyet", "Toplam Maliyet"])

    df_gosterim = df.copy()
    df_gosterim["Toplam Maliyet"] = df_gosterim["Stok Adedi"] * df_gosterim["Birim Maliyet"]

    df_gosterim["Stok Adedi"] = df_gosterim["Stok Adedi"].apply(
        lambda x: int(x) if float(x).is_integer() else x
    )
    df_gosterim["Birim Maliyet"] = df_gosterim["Birim Maliyet"].apply(format_tl)
    df_gosterim["Toplam Maliyet"] = df_gosterim["Toplam Maliyet"].apply(format_tl)

    return df_gosterim


def stok_toplam_maliyet_hesapla(df: pd.DataFrame) -> float:
    """Toplam stok maliyetini hesaplar."""
    if df.empty:
        return 0.0
    return float((df["Stok Adedi"] * df["Birim Maliyet"]).sum())


def stok_toplam_adet_hesapla(df: pd.DataFrame) -> int:
    """Toplam ürün adedini hesaplar."""
    if df.empty:
        return 0
    return int(df["Stok Adedi"].sum())


# -----------------------------
# CSV dosyalarını hazırla
# -----------------------------
csv_dosyalarini_hazirla()


# -----------------------------
# Dinamik veriler
# -----------------------------
satislar_df = satislari_oku()
giderler_df = giderleri_oku()
stok_df = stok_oku()

bu_ay_satis = bu_ay_toplam_hesapla(satislar_df)
bu_ay_toplam_gider = bu_ay_toplam_hesapla(giderler_df)
bu_ay_net_kar = bu_ay_satis - bu_ay_toplam_gider

toplam_stok_maliyeti = stok_toplam_maliyet_hesapla(stok_df)
toplam_urun_adedi = stok_toplam_adet_hesapla(stok_df)
toplam_kayitli_urun = len(stok_df.index)

satislar_gosterim_df = tablo_gosterime_hazirla(satislar_df, "Tutar")
giderler_gosterim_df = tablo_gosterime_hazirla(giderler_df, "Tutar")
stok_detay_gosterim_df = stok_tablo_gosterime_hazirla(stok_df)


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

        p, label, div, span {
            color: #1f2937;
        }

        /* Mobil dark mode / tüm inputlar için kesin düzeltme */
        input, textarea, select {
            color: #111827 !important;
            background-color: #ffffff !important;
            -webkit-text-fill-color: #111827 !important;
            caret-color: #111827 !important;
        }

        input::placeholder,
        textarea::placeholder,
        select::placeholder {
            color: #6b7280 !important;
            -webkit-text-fill-color: #6b7280 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div,
        .stDateInput > div > div {
            border-radius: 14px !important;
            border: 1px solid rgba(15, 23, 42, 0.08) !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] div,
        .stDateInput input {
            color: #111827 !important;
            background-color: #ffffff !important;
            -webkit-text-fill-color: #111827 !important;
            caret-color: #111827 !important;
        }

        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder,
        div[data-baseweb="select"] input::placeholder,
        .stDateInput input::placeholder {
            color: #6b7280 !important;
            -webkit-text-fill-color: #6b7280 !important;
            opacity: 1 !important;
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

        /* Butonlar */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button,
        [data-testid="stDownloadButton"] > button {
            width: 100%;
            border-radius: 14px;
            border: none;
            background: linear-gradient(135deg, #111827 0%, #374151 100%);
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 700;
            padding: 0.72rem 1rem;
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.18);
            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 28px rgba(17, 24, 39, 0.24);
            background: linear-gradient(135deg, #0f172a 0%, #1f2937 100%);
        }

        .stButton > button:focus,
        [data-testid="stFormSubmitButton"] > button:focus,
        [data-testid="stDownloadButton"] > button:focus {
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
# Sidebar / RBAC
# -----------------------------
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.title("📂 Menü")

rol = st.session_state.get("role", "")

if rol == "admin":
    kullanilabilir_sayfalar = ADMIN_SAYFALARI
    varsayilan_index = 0
elif rol == "staff":
    kullanilabilir_sayfalar = STAFF_SAYFALARI
    varsayilan_index = 0
else:
    kullanilabilir_sayfalar = []
    varsayilan_index = 0

if not kullanilabilir_sayfalar:
    st.error("Bu kullanıcı için yetki tanımlı değil.")
    st.stop()

sayfa = st.sidebar.radio(
    "Sayfa Seçin",
    kullanilabilir_sayfalar,
    index=varsayilan_index
)

if rol == "staff" and sayfa not in STAFF_SAYFALARI:
    sayfa = "Veri Girişi"

st.sidebar.markdown("---")
st.sidebar.caption("Baros Yönetim Sistemi")
st.sidebar.caption("Premium demo arayüz")
st.sidebar.caption(f"Giriş yapan kullanıcı: {st.session_state.get('username', '')}")
st.sidebar.caption(f"Rol: {st.session_state.get('role', '')}")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Çıkış Yap"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# -----------------------------
# Sayfalar
# -----------------------------
if sayfa == "Ana Panel":
    st.title("📊 Ana Panel")
    st.caption("Toptan tekstil şirketi için kâr/zarar ve depo değerleme odaklı yönetici ekranı")

    # Dış sistem şablonu
    gerekli_kolonlar = [
        "Ürün Kategori",
        "Sezon",
        "Ürün Adı",
        "Birim Satış Fiyatı (TL)",
        "Birim Üretim Maliyeti (TL)",
        "Satılan Adet",
        "Depodaki Kalan Adet",
    ]

    with st.expander("📥 Dış Sistemden Veri Yükle (Excel/CSV)", expanded=False):
        ornek_df = pd.DataFrame(
            {
                "Ürün Kategori": ["Gömlek", "Mont"],
                "Sezon": ["İlkbahar 2026", "Kış 2025"],
                "Ürün Adı": ["Slim Fit Poplin Gömlek", "Kapitone Şişme Mont"],
                "Birim Satış Fiyatı (TL)": [720, 1450],
                "Birim Üretim Maliyeti (TL)": [410, 920],
                "Satılan Adet": [980, 410],
                "Depodaki Kalan Adet": [260, 95],
            }
        )

        st.download_button(
            label="📄 Örnek CSV Şablonunu İndir",
            data=ornek_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="erp_dashboard_ornek_sablon.csv",
            mime="text/csv"
        )

        yuklenen_dosya = st.file_uploader(
            "Excel veya CSV dosyanızı yükleyin",
            type=["csv", "xlsx"]
        )

    # Varsayılan demo veri
    demo_erp_df = pd.DataFrame(
        {
            "Ürün Adı": [
                "Slim Fit Poplin Gömlek",
                "Oduncu Ekose Gömlek",
                "Kapitone Şişme Mont",
                "Kaşe Kaban",
                "Oversize Sweatshirt",
                "Basic Kapüşonlu Sweat",
                "Waffle Tişört",
                "Premium Bisiklet Yaka Tişört",
                "Likralı Klasik Pantolon",
                "Jogger Kargo Pantolon",
            ],
            "Ürün Kategori": [
                "Gömlek",
                "Gömlek",
                "Mont",
                "Mont",
                "Sweatshirt",
                "Sweatshirt",
                "Tişört",
                "Tişört",
                "Pantolon",
                "Pantolon",
            ],
            "Sezon": [
                "Kış 2025",
                "İlkbahar 2026",
                "Kış 2025",
                "Kış 2025",
                "İlkbahar 2026",
                "Kış 2025",
                "Yaz 2026",
                "Yaz 2026",
                "İlkbahar 2026",
                "Yaz 2026",
            ],
            "Birim Satış Fiyatı (TL)": [720, 810, 1450, 1680, 790, 860, 420, 470, 980, 1040],
            "Birim Üretim Maliyeti (TL)": [410, 465, 920, 1080, 510, 560, 210, 245, 620, 670],
            "Satılan Adet": [980, 760, 410, 265, 690, 530, 1420, 1160, 420, 380],
            "Depodaki Kalan Adet": [260, 210, 95, 60, 180, 145, 320, 280, 110, 90],
        }
    )

    erp_df = demo_erp_df.copy()
    veri_kaynagi_demo = True

    if yuklenen_dosya is not None:
        try:
            dosya_adi = yuklenen_dosya.name.lower()

            if dosya_adi.endswith(".csv"):
                yuklenen_df = pd.read_csv(yuklenen_dosya)
            else:
                yuklenen_df = pd.read_excel(yuklenen_dosya)

            eksik_kolonlar = [kolon for kolon in gerekli_kolonlar if kolon not in yuklenen_df.columns]

            if eksik_kolonlar:
                st.error(
                    "Yüklenen dosyada eksik kolonlar var: " + ", ".join(eksik_kolonlar)
                )
                st.info("Lütfen örnek şablonu indirip aynı kolon yapısıyla yükleyin.")
                erp_df = demo_erp_df.copy()
                veri_kaynagi_demo = True
            else:
                erp_df = yuklenen_df[gerekli_kolonlar].copy()

                for kolon in [
                    "Birim Satış Fiyatı (TL)",
                    "Birim Üretim Maliyeti (TL)",
                    "Satılan Adet",
                    "Depodaki Kalan Adet",
                ]:
                    erp_df[kolon] = pd.to_numeric(erp_df[kolon], errors="coerce").fillna(0)

                erp_df["Ürün Kategori"] = erp_df["Ürün Kategori"].astype(str)
                erp_df["Sezon"] = erp_df["Sezon"].astype(str)
                erp_df["Ürün Adı"] = erp_df["Ürün Adı"].astype(str)
                veri_kaynagi_demo = False

        except Exception as e:
            st.error(f"Dosya okunurken bir hata oluştu: {e}")
            st.info("Lütfen dosya biçiminizi kontrol edin veya örnek şablonu kullanın.")
            erp_df = demo_erp_df.copy()
            veri_kaynagi_demo = True

    if veri_kaynagi_demo:
        st.warning("Şu an Demo (Örnek) verisi görüyorsunuz. Kendi verilerinizi yukarıdan yükleyin.")

    # Üst filtre satırı
    filtre_sol, filtre_sag = st.columns(2)

    tum_kategoriler = sorted(erp_df["Ürün Kategori"].dropna().unique().tolist())
    tum_sezonlar = sorted(erp_df["Sezon"].dropna().unique().tolist())

    with filtre_sol:
        secilen_kategoriler = st.multiselect(
            "Kategori Seçimi",
            options=tum_kategoriler,
            default=[]
        )

    with filtre_sag:
        secilen_sezonlar = st.multiselect(
            "Sezon Seçimi",
            options=tum_sezonlar,
            default=[]
        )

    # Filtreleme
    filtrelenmis_df = erp_df.copy()

    if secilen_kategoriler:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Ürün Kategori"].isin(secilen_kategoriler)]

    if secilen_sezonlar:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Sezon"].isin(secilen_sezonlar)]

    # Temel iş hesapları
    filtrelenmis_df["Toplam Ciro (TL)"] = filtrelenmis_df["Birim Satış Fiyatı (TL)"] * filtrelenmis_df["Satılan Adet"]
    filtrelenmis_df["Satılan Malın Maliyeti (TL)"] = filtrelenmis_df["Birim Üretim Maliyeti (TL)"] * filtrelenmis_df["Satılan Adet"]
    filtrelenmis_df["Net Ürün Kârı (TL)"] = filtrelenmis_df["Toplam Ciro (TL)"] - filtrelenmis_df["Satılan Malın Maliyeti (TL)"]
    filtrelenmis_df["Depodaki Malın Değeri (TL)"] = filtrelenmis_df["Birim Üretim Maliyeti (TL)"] * filtrelenmis_df["Depodaki Kalan Adet"]

    toplam_ciro = filtrelenmis_df["Toplam Ciro (TL)"].sum() if not filtrelenmis_df.empty else 0
    satilan_malin_maliyeti = filtrelenmis_df["Satılan Malın Maliyeti (TL)"].sum() if not filtrelenmis_df.empty else 0
    net_urun_kari = filtrelenmis_df["Net Ürün Kârı (TL)"].sum() if not filtrelenmis_df.empty else 0
    depodaki_malin_degeri = filtrelenmis_df["Depodaki Malın Değeri (TL)"].sum() if not filtrelenmis_df.empty else 0

    # Kategori bazlı analiz
    kategori_df = (
        filtrelenmis_df.groupby("Ürün Kategori", as_index=False)[
            ["Toplam Ciro (TL)", "Satılan Malın Maliyeti (TL)", "Depodaki Malın Değeri (TL)"]
        ]
        .sum()
        if not filtrelenmis_df.empty
        else pd.DataFrame(columns=["Ürün Kategori", "Toplam Ciro (TL)", "Satılan Malın Maliyeti (TL)", "Depodaki Malın Değeri (TL)"])
    )

    st.markdown("###")

    # Üst satır kartlar
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        summary_card("Toplam Ciro", format_tl(toplam_ciro), "💸", "#ffffff")

    with col2:
        summary_card("Satılan Malın Maliyeti", format_tl(satilan_malin_maliyeti), "🏭", "#ffffff")

    with col3:
        summary_card("Net Ürün Kârı", format_tl(net_urun_kari), "📈", "#ffffff")

    with col4:
        summary_card("Depodaki Malın Değeri", format_tl(depodaki_malin_degeri), "📦", "#ffffff")

    st.markdown("###")

    # Orta satır grafikler
    grafik_sol, grafik_sag = st.columns(2)

    with grafik_sol:
        st.subheader("Kategori Bazlı Ciro vs Maliyet")

        if kategori_df.empty:
            st.info("Seçilen filtreler için gösterilecek veri bulunamadı.")
        else:
            kategori_grafik_df = kategori_df.melt(
                id_vars="Ürün Kategori",
                value_vars=["Toplam Ciro (TL)", "Satılan Malın Maliyeti (TL)"],
                var_name="Gösterge",
                value_name="Tutar"
            )

            fig_ciro_maliyet = px.bar(
                kategori_grafik_df,
                x="Ürün Kategori",
                y="Tutar",
                color="Gösterge",
                barmode="group",
                text_auto=".2s"
            )
            fig_ciro_maliyet.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#111827"),
                legend_title_text="Gösterge",
                xaxis_title="Ürün Kategori",
                yaxis_title="Tutar (TL)"
            )
            fig_ciro_maliyet.update_xaxes(showgrid=False)
            fig_ciro_maliyet.update_yaxes(gridcolor="rgba(17,24,39,0.08)")
            st.plotly_chart(fig_ciro_maliyet, use_container_width=True)

    with grafik_sag:
        st.subheader("Depodaki Malın Değeri Dağılımı")

        if kategori_df.empty:
            st.info("Seçilen filtreler için gösterilecek veri bulunamadı.")
        else:
            fig_stok_deger = px.pie(
                kategori_df,
                names="Ürün Kategori",
                values="Depodaki Malın Değeri (TL)",
                hole=0.58
            )
            fig_stok_deger.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#111827"),
                legend_title_text="Kategori"
            )
            st.plotly_chart(fig_stok_deger, use_container_width=True)

    st.markdown("###")

    # Alt satır detay tablo
    st.subheader("Ürün Bazlı Karlılık ve Depo Değerleme Detayı")

    if filtrelenmis_df.empty:
        st.info("Seçilen filtreler için tablo verisi bulunamadı.")
    else:
        detay_df = filtrelenmis_df[
            [
                "Ürün Adı",
                "Ürün Kategori",
                "Sezon",
                "Birim Satış Fiyatı (TL)",
                "Birim Üretim Maliyeti (TL)",
                "Satılan Adet",
                "Depodaki Kalan Adet",
                "Toplam Ciro (TL)",
                "Satılan Malın Maliyeti (TL)",
                "Net Ürün Kârı (TL)",
                "Depodaki Malın Değeri (TL)",
            ]
        ].copy()

        for kolon in [
            "Birim Satış Fiyatı (TL)",
            "Birim Üretim Maliyeti (TL)",
            "Toplam Ciro (TL)",
            "Satılan Malın Maliyeti (TL)",
            "Net Ürün Kârı (TL)",
            "Depodaki Malın Değeri (TL)",
        ]:
            detay_df[kolon] = detay_df[kolon].apply(format_tl)

        st.dataframe(detay_df, use_container_width=True, hide_index=True)

elif sayfa == "Stok Değerleme":
    st.title("📦 Stok Değerleme")
    st.caption("Stok verileri stok.csv dosyasından okunur")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Toplam Stok Maliyeti", format_tl(toplam_stok_maliyeti))
    with c2:
        st.metric("Toplam Kayıtlı Ürün", str(toplam_kayitli_urun))
    with c3:
        st.metric("Toplam Ürün Adedi", str(toplam_urun_adedi))

    st.markdown("### Stok Detayları")
    st.dataframe(stok_detay_gosterim_df, use_container_width=True, hide_index=True)

elif sayfa == "Cari":
    st.title("💸 Cari Hesaplar & Nakit Akışı")
    st.caption("B2B toptan erkek giyim operasyonu için müşteri alacakları ve tedarikçi borç yönetimi")

    musteri_df = pd.DataFrame(
        {
            "Müşteri Adı": [
                "Yıldız Erkek Giyim",
                "Karaköy Butik",
                "Mavi Adam Store",
                "Ankara Trend Menswear",
                "İzmir Premium Giyim",
                "Bursa Moda Erkek",
            ],
            "Toplam Satış (TL)": [480000, 365000, 520000, 295000, 410000, 275000],
            "Tahsil Edilen (TL)": [320000, 210000, 400000, 150000, 265000, 175000],
            "Vade Durumu": [
                "Vadesi Yaklaşıyor",
                "Gecikmiş",
                "Normal",
                "Gecikmiş",
                "Normal",
                "Vadesi Yaklaşıyor",
            ],
        }
    )
    musteri_df["Kalan Bakiye (TL)"] = musteri_df["Toplam Satış (TL)"] - musteri_df["Tahsil Edilen (TL)"]

    tedarikci_df = pd.DataFrame(
        {
            "Tedarikçi Adı": [
                "Aydın Kumaşçılık",
                "Kardeşler Fason Atölye",
                "Düğmeci Ali",
                "Marmara Etiket",
                "Ege Ambalaj",
            ],
            "Toplam Borç (TL)": [390000, 285000, 72000, 54000, 46000],
            "Ödenen (TL)": [210000, 120000, 35000, 18000, 12000],
            "Vade Tarihi": [
                "10.04.2026",
                "15.04.2026",
                "08.04.2026",
                "18.04.2026",
                "22.04.2026",
            ],
        }
    )
    tedarikci_df["Kalan Borç (TL)"] = tedarikci_df["Toplam Borç (TL)"] - tedarikci_df["Ödenen (TL)"]

    toplam_musteri_alacagi_cari = float(musteri_df["Kalan Bakiye (TL)"].sum())
    toplam_tedarikci_borcu_cari = float(tedarikci_df["Kalan Borç (TL)"].sum())
    net_nakit_pozisyonu = toplam_musteri_alacagi_cari - toplam_tedarikci_borcu_cari

    st.markdown("###")

    kart1, kart2, kart3 = st.columns(3)

    with kart1:
        summary_card(
            "Toplam Müşteri Alacağı",
            format_tl(toplam_musteri_alacagi_cari),
            "🧾",
            "#ffffff"
        )

    with kart2:
        summary_card(
            "Toplam Tedarikçi Borcu",
            format_tl(toplam_tedarikci_borcu_cari),
            "🏷️",
            "#ffffff"
        )

    with kart3:
        summary_card(
            "Net Nakit Pozisyonu",
            format_tl(net_nakit_pozisyonu),
            "💰",
            "#ffffff"
        )

    st.markdown("###")

    sol, sag = st.columns(2)

    with sol:
        st.subheader("Müşteri Alacakları")
        musteri_gosterim_df = musteri_df.copy()
        for kolon in ["Toplam Satış (TL)", "Tahsil Edilen (TL)", "Kalan Bakiye (TL)"]:
            musteri_gosterim_df[kolon] = musteri_gosterim_df[kolon].apply(format_tl)
        st.dataframe(musteri_gosterim_df, use_container_width=True, hide_index=True)

    with sag:
        st.subheader("Tedarikçi Borçları")
        tedarikci_gosterim_df = tedarikci_df.copy()
        for kolon in ["Toplam Borç (TL)", "Ödenen (TL)", "Kalan Borç (TL)"]:
            tedarikci_gosterim_df[kolon] = tedarikci_gosterim_df[kolon].apply(format_tl)
        st.dataframe(tedarikci_gosterim_df, use_container_width=True, hide_index=True)

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
    st.caption("Yeni satış, gider ve stok kayıtlarını CSV dosyalarına ekleyin")

    if "bildirim_mesaji" in st.session_state:
        st.success(st.session_state.pop("bildirim_mesaji"))

    sol, orta, sag = st.columns(3)

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
                    st.session_state["bildirim_mesaji"] = "Yeni satış başarıyla kaydedildi."
                    st.rerun()

    with orta:
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
                    st.session_state["bildirim_mesaji"] = "Yeni gider başarıyla kaydedildi."
                    st.rerun()

    with sag:
        st.subheader("Yeni Ürün / Stok Ekle")
        with st.form("yeni_stok_formu", clear_on_submit=True):
            urun_kodu = st.text_input("Ürün Kodu", key="urun_kodu")
            urun_adi = st.text_input("Ürün Adı", key="urun_adi")
            kategori = st.text_input("Kategori", key="kategori")
            stok_adedi = st.number_input(
                "Stok Adedi",
                min_value=0,
                step=1,
                key="stok_adedi"
            )
            birim_maliyet = st.number_input(
                "Birim Maliyet",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="birim_maliyet"
            )

            stok_submit = st.form_submit_button("Ürünü / Stoğu Kaydet")

            if stok_submit:
                if not urun_kodu.strip() or not urun_adi.strip() or not kategori.strip():
                    st.error("Lütfen tüm ürün alanlarını doldurun.")
                else:
                    yeni_stok = pd.DataFrame(
                        [{
                            "Ürün Kodu": urun_kodu.strip(),
                            "Ürün Adı": urun_adi.strip(),
                            "Kategori": kategori.strip(),
                            "Stok Adedi": stok_adedi,
                            "Birim Maliyet": birim_maliyet
                        }]
                    )
                    yeni_stok.to_csv(
                        STOK_DOSYA,
                        mode="a",
                        header=False,
                        index=False,
                        encoding="utf-8-sig"
                    )
                    st.session_state["bildirim_mesaji"] = "Yeni ürün / stok başarıyla kaydedildi."
                    st.rerun()

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