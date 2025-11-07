import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (
    SUPPORTED_COUNTRIES, country_name_to_code,
    fetch_comtrade, search_firms_local, fetch_opentradestats,
    load_favorites, save_favorites
)
import os, json

# --- Authentication ---
def check_auth():
    # First try Streamlit secrets
    try:
        secrets = st.secrets
        user = secrets.get("AUTH_USER")
        pwd = secrets.get("AUTH_PWD")
    except Exception:
        user = pwd = None
    # Fallback to local config (config.toml values via env or file)
    if not user or not pwd:
        user = os.environ.get("GULEROGLU_USER", "guleroglu")
        pwd = os.environ.get("GULEROGLU_PWD", "2025export")
    return user, pwd

AUTH_USER, AUTH_PWD = check_auth()

st.set_page_config(page_title="GulerogluTrade", layout="wide")
st.title("GulerogluTrade — Güvenli Girişli Ticaret Araçları")

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if username == AUTH_USER and password == AUTH_PWD:
            st.session_state.logged_in = True
            st.success("Giriş başarılı!")
        else:
            st.error("Yanlış kullanıcı adı veya şifre.")
    st.stop()

# --- Main app ---
st.markdown("Hoşgeldin! GulerogluTrade ile ülke, HS kodu veya firma adı ile sorgula. (Kaynak: UN Comtrade + demo firmalar)")

with st.sidebar:
    st.header("Sorgu Ayarları")
    country = st.selectbox("Hedef Ülke", options=sorted(SUPPORTED_COUNTRIES.keys()), index=0)
    year = st.selectbox("Yıl", options=list(range(2018, 2026)), index=5)
    flow = st.selectbox("Akış", options={"İthalat":"M","İhracat":"X"}, index=0)
    query_type = st.radio("Sorgu Türü", options=["HS Kodu / Ürün","Firma Adı"])
    if query_type == "HS Kodu / Ürün":
        hs = st.text_input("HS Kodu (örn. 0805)", value="0805")
        firm_query = ""
    else:
        firm_query = st.text_input("Firma adı (ör. 'MPM Fruit')", value="")
        hs = ""
    use_live = st.checkbox("Canlı API kullan (UN Comtrade)", value=True)
    st.markdown("---")
    st.markdown("Favoriler:")
    favorites = load_favorites()
    for i, fav in enumerate(favorites):
        st.write(f"{i+1}. {fav.get('label')} — {fav.get('query')}")

col1, col2 = st.columns([3,1])

with col1:
    st.subheader("Sorgu Sonuçları")
    if st.button("Sorgula"):
        st.info(f"Sorgulanıyor: {country} | {year} | { 'Firma: '+firm_query if firm_query else 'HS: '+hs }")
        reporter_code = country_name_to_code(country)
        df = None
        # If HS query, use UN Comtrade
        if hs:
            if use_live:
                df = fetch_comtrade(reporter=reporter_code, period=str(year), cmdCode=hs, flowCode=flow, partnerCode="all")
            if df is None or df.empty:
                st.warning("UN Comtrade'dan veri gelmedi veya boş. Örnek/önbellek verisi gösteriliyor.")
                df = pd.read_csv(os.path.join(os.path.dirname(__file__), "sample_serbia_citrus.csv"))
        else:
            # firm query: try OpenTradeStats (live) then fallback to local sample
            df = fetch_opentradestats(country=country, year=year, firm_name=firm_query)
            if df is None or df.empty:
                st.warning("Firma bazlı canlı veri bulunamadı. Yerel örnek veri ile arama yapılıyor.")
                df = search_firms_local(firm_query)
        st.write(f"Toplam kayıt: {len(df)}")
        st.dataframe(df.head(200))

        # aggregate by partner if available
        if "partnerDesc" in df.columns and "primaryValue" in df.columns:
            agg = df.groupby("partnerDesc", dropna=False)["primaryValue"].sum().reset_index().sort_values("primaryValue", ascending=False)
            st.subheader("Ülke Bazlı Toplam Değer (USD)")
            fig = px.bar(agg, x="partnerDesc", y="primaryValue", labels={"primaryValue":"Değer (USD)","partnerDesc":"Partner Ülke"})
            st.plotly_chart(fig, use_container_width=True)
        # download
        st.download_button("CSV olarak indir", df.to_csv(index=False).encode('utf-8'), file_name=f"guleroglu_{country}_{year}.csv", mime='text/csv')
        # save favorite
        if st.button("Favori olarak kaydet"):
            label = st.text_input("Favori etiketi (ör. 'RS Narenciye Turkey')", value=f"{country}_{hs or firm_query}_{year}")
            fav = {"label": label, "country": country, "year": year, "query": hs or firm_query, "type": "HS" if hs else "FIRM"}
            save_favorites(fav)
            st.success("Favori kaydedildi. Yeniden yükleyin.")


with col2:
    st.subheader("Bilgi / İpuçları")
    st.markdown("""
    - **Canlı veri:** UN Comtrade API bazen rate-limit uygulayabilir. Firma bazlı güçlü sorgular OpenTradeStats/ImportYeti gibi kaynaklardan gelir (bazıları ücretli).
    - **Demo modu:** Eğer canlı veri gelmezse uygulama sample veriyi kullanır.
    - **Veri doğrulama:** Önemli alımlar için mutlaka doğrudan referans talep et.
    """)
    st.markdown("---")
    st.subheader("Favori Yönetimi")
    if st.button("Favorileri temizle"):
        save_favorites([])
        st.success("Favoriler temizlendi. Yeniden yükleyin.")
    st.markdown("---")
    st.subheader("Destek")
    st.markdown("Uygulamayı GitHub'a push edip Streamlit Cloud üzerinden deploy edebilirsiniz. README'de adımlar var.")

st.caption("GulerogluTrade — UN Comtrade + OpenTradeStats (placeholder).")