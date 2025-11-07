import streamlit as st
import pandas as pd
import plotly.express as px
import os
from utils import SUPPORTED_COUNTRIES, country_name_to_code, fetch_comtrade, search_firms_local, load_favorites, save_favorites

st.set_page_config(page_title="GulerogluTrade v2", layout="wide", initial_sidebar_state="expanded")

# --- Simple auth (uses Streamlit secrets or env as before) ---
def check_auth():
    try:
        secrets = st.secrets
        user = secrets.get("AUTH_USER")
        pwd = secrets.get("AUTH_PWD")
    except Exception:
        user = pwd = None
    if not user or not pwd:
        user = os.environ.get("GULEROGLU_USER", "guleroglu")
        pwd = os.environ.get("GULEROGLU_PWD", "2025export")
    return user, pwd

AUTH_USER, AUTH_PWD = check_auth()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("# GulerogluTrade — Giriş")
    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")

    def login():
        if username == st.secrets.get("AUTH_USER", "guleroglu") and password == st.secrets.get("AUTH_PWD", "2025export"):
            st.session_state.logged_in = True

    st.button("Giriş", on_click=login)
    st.stop()

st.markdown("# GulerogluTrade v2")
st.markdown("HS kodu veya firma adı ile arama yap — filtreleyip CSV indir. Kaynak: UN Comtrade + demo firma verisi.")

# Sidebar filters
with st.sidebar:
    st.header("Arama ve Filtreler")
    country = st.selectbox("Hedef ülke", options=["Tümü"] + sorted(SUPPORTED_COUNTRIES.keys()), index=0)
    year = st.selectbox("Yıl", options=list(range(2018, 2026)), index=5)
    flow = st.selectbox("Akış", options={"İthalat":"M","İhracat":"X"}, index=0)
    query_type = st.radio("Arama türü", options=["HS Kodu / Ürün","Firma Adı"], index=0)
    if query_type == "HS Kodu / Ürün":
        hs = st.text_input("HS Kodu (örn. 0805)", value="0805")
        firm_q = ""
    else:
        firm_q = st.text_input("Firma adı (örn. MPM Fruit)", value="")
        hs = ""
    use_live = st.checkbox("Canlı UN Comtrade kullan (HS sorguları için)", value=True)
    st.markdown("---")
    st.subheader("Favoriler")
    favs = load_favorites()
    for i, f in enumerate(favs):
        st.write(f"{i+1}. {f.get('label')} — {f.get('query')}")

# Main area
col1, col2 = st.columns([3,1])
with col1:
    st.subheader("Arama Sonuçları")
    if st.button("Sorgula"):
        st.info(f"Sorgulanıyor: {country} | {year} | { 'Firma: '+firm_q if firm_q else 'HS: '+hs }")
        df = pd.DataFrame()
        # If HS search, use UN Comtrade preview API (for selected country or all)
        if hs:
            reporter = country_name_to_code(country) if country != "Tümü" else "688"  # fallback Serbia if All
            if use_live:
                df = fetch_comtrade(reporter=reporter, period=str(year), cmdCode=hs, flowCode=flow, partnerCode="all")
            if df is None or df.empty:
                st.warning("Canlı UN Comtrade verisi gelmedi veya boş. Örnek veri gösteriliyor.")
                df = pd.read_csv(os.path.join(os.path.dirname(__file__), "sample_serbia_citrus.csv"))
        else:
            # firm search
            df = search_firms_local(firm_q)
            if country != "Tümü":
                df = df[df["country"]==country]
            if df is None or df.empty:
                st.warning("Firma bazlı sonuç bulunamadı.")
                df = pd.DataFrame(columns=["year","country","firm_name","partnerDesc","product","primaryValue","netWeight"])
        st.write(f"Toplam kayıt: {len(df)}")
        # show table and allow CSV download
        if not df.empty:
            display_cols = [c for c in ["year","country","firm_name","partnerDesc","product","cmdCode","cmdDesc","flowDesc","primaryValue","netWeight","qtyUnitAbbr"] if c in df.columns]
            st.dataframe(df[display_cols].head(300))
            st.download_button("CSV indir", df.to_csv(index=False).encode("utf-8"), file_name=f"guleroglu_results_{country}_{year}.csv", mime="text/csv")
            # quick aggregation for HS results
            if "partnerDesc" in df.columns and "primaryValue" in df.columns:
                agg = df.groupby("partnerDesc", dropna=False)["primaryValue"].sum().reset_index().sort_values("primaryValue", ascending=False)
                st.subheader("Partner Ülke Bazlı Toplam Değer (USD)")
                fig = px.bar(agg, x="partnerDesc", y="primaryValue", labels={"partnerDesc":"Partner Ülke","primaryValue":"Değer (USD)"})
                st.plotly_chart(fig, use_container_width=True)
            # save favorite
            if st.button("Favori kaydet"):
                label = st.text_input("Favori etiketi", value=f"{country}_{hs or firm_q}_{year}")
                fav = {"label": label, "country": country, "year": year, "query": hs or firm_q, "type": "HS" if hs else "FIRM"}
                save_favorites(fav)
                st.success("Favori kaydedildi.")
    else:
        st.info("Arama yapmak için sol menüde kriterleri seçip 'Sorgula' butonuna bas.")

with col2:
    st.subheader("Notlar ve İpuçları")
    st.markdown("""
    - UN Comtrade canlı servisi zaman zaman sınırlama yapabilir. Eğer sonuç yoksa örnek veri gösterilir.
    - Firma bazlı güçlü veriler için ImportYeti / OpenTradeStats gibi servislerin API anahtarı eklenirse canlı sonuç alınır.
    - Arama sonrası CSV indirip Excel'de detaylı analiz yapabilirsin.
    """)
    st.markdown("---")
    st.subheader("Favoriler Yönetimi")
    if st.button("Favorileri temizle"):
        save_favorites([])
        st.success("Favoriler temizlendi.")

st.caption("GulerogluTrade v2 — Hazır demo. Daha fazla entegrasyon istersen eklerim.")
