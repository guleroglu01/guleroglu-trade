# GulerogluTrade Ultimate — Secure Web-ready Package

Bu paket Streamlit Cloud üzerinde deploy edilebilecek, şifreli giriş kullanan **GulerogluTrade Ultimate** uygulamasının GitHub-ready sürümüdür.

## Öne çıkanlar
- Giriş ekranı: kullanıcı adı ve şifre kontrolü için **Streamlit Secrets** kullanımı (önerilen) ve yerel fallback.
- Varsayılan kimlik bilgileri (sadece örnek): kullanıcı=`guleroglu`, şifre=`2025export`
- 15 ülke için HS ve firma bazlı sorgu (UN Comtrade + demo veri)
- Favori yönetimi (local JSON)
- Türkçe arayüz

## Nasıl yüklenir (GitHub -> Streamlit Cloud)
1. GitHub hesabında yeni repo oluştur (ör. `guleroglu-trade`) ve bu dosyaları yükle.
2. Streamlit Community Cloud'a giriş yap, "New app" -> GitHub repo'nu seç.
3. Advanced settings -> "Runtime secrets" bölümüne şu iki anahtarı ekle:
   - AUTH_USER = guleroglu
   - AUTH_PWD = 2025export
4. Deploy et. Uygulama açıldığında giriş ekranı gelecektir.

## Lokal çalıştırma (geliştirme)
1. Python 3.10+ kur.
2. Sanal ortam oluştur ve bağımlılıkları yükle:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```
3. Lokal test için environment değişkenleri kullanabilirsin:
```bash
export GULEROGLU_USER=guleroglu
export GULEROGLU_PWD=2025export
streamlit run app.py
```
(Windows PowerShell: `$env:GULEROGLU_USER="guleroglu"` vb.)

## Canlı API entegrasyonu
- `utils.fetch_opentradestats` fonksiyonuna gerçek API anahtarları eklendiğinde firma bazlı canlı veriler çekilecektir.
- UN Comtrade preview API zaten kullanılıyor; rate-limit olabilir.

## Notlar güvenlik
- Streamlit Secrets kullanımı önerilir; böylece şifre GitHub'da görünmez.
- Secrets eklenmezse uygulama varsayılan lokal şifreyi (2025export) kullanır — canlı ortamda secrets eklemeyi unutma.
