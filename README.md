# GulerogluTrade v2 - Local & Streamlit-ready

GulerogluTrade v2, HS kodu ve firma adıyla arama yapabilen, 15 ülkeyi destekleyen Streamlit uygulamasıdır. Türkçe arayüzlü, mobil uyumlu demo versiyonudur.

## Hızlı kurulum (lokal)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Cloud)
- Repo'yu GitHub'a yükleyin.
- Streamlit Cloud'dan "New app" ile repo seçin.
- Runtime secrets (AUTH_USER, AUTH_PWD) ekleyin.

## Notlar
- UN Comtrade preview API kullanılıyor. Rate limit durumunda örnek veri görüntülenir.
- Firma bazlı canlı veri için OpenTradeStats/ImportYeti entegrasyonu eklenebilir.
