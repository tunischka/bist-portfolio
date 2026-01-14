# BIST Portfolio SaaS

Modern, çoklu kullanıcılı BIST (Borsa İstanbul) portföy takip uygulaması.

## 🚀 Özellikler

- ✅ Çoklu kullanıcı desteği (Multi-tenancy)
- ✅ Firebase Authentication ile güvenli giriş
- ✅ Firestore veritabanı
- ✅ Gerçek zamanlı BIST hisse fiyatları (yfinance)
- ✅ Ağırlıklı ortalama maliyet hesaplama
- ✅ Portföy kar/zarar takibi
- ✅ İşlem geçmişi (Transaction history)

## 📋 Gereksinimler

- Python 3.8+
- Firebase projesi (Firestore + Authentication)

## 🛠️ Kurulum

### 1. Firebase Projesini Oluştur

Detaylı adımlar için `firebase_setup_guide.md` dosyasına bakın.

**Özet:**
1. [Firebase Console](https://console.firebase.google.com/) → Yeni proje oluştur
2. Firestore Database'i aktif et (test mode)
3. Authentication'ı aktif et (Email/Password)
4. Service Account anahtarını indir (`serviceAccountKey.json`)

### 2. Projeyi Kur

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Firebase anahtarını ekle
# serviceAccountKey.json dosyasını proje kök dizinine kopyala
```

### 3. Environment Variables (Opsiyonel)

`.env` dosyası oluştur:
```
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
```

### 4. Uygulamayı Çalıştır

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine git.

## 📁 Proje Yapısı

```
borsacım/
├── app.py                  # Ana uygulama
├── requirements.txt
├── .env.example
├── serviceAccountKey.json  # Firebase anahtarı (GİZLİ!)
├── src/
│   ├── auth/              # Authentication
│   │   ├── firebase_auth.py
│   │   └── session.py
│   ├── db/                # Database
│   │   ├── firestore_client.py
│   │   ├── models.py
│   │   └── repositories.py
│   ├── services/          # Business logic
│   │   ├── portfolio_calculator.py
│   │   └── stock_data.py
│   └── ui/                # User interface
│       └── pages/
│           ├── login.py
│           ├── register.py
│           ├── dashboard.py
│           └── portfolio.py
```

## 💡 Kullanım

### 1. Kayıt Ol / Giriş Yap
- Yeni hesap oluştur veya mevcut hesapla giriş yap

### 2. Portföy Oluştur
- Dashboard'dan "Yeni Portföy Oluştur" ile portföy ekle

### 3. İşlem Ekle
- Portföy detayına gir
- "Yeni İşlem Ekle" ile BUY/SELL işlemi kaydet
- BIST hisse kodları: THYAO, GARAN, ISCTR, vb. (otomatik ".IS" eklenir)

### 4. Portföyünü Takip Et
- Mevcut pozisyonlarını gör
- Kar/zarar hesaplamalarını izle
- İşlem geçmişini incele

### 5. Debug Mode & Yenileme
- **Debug Mode:** Portföy sayfasında "🐛 Debug" butonu - veri kaynağı bilgilerini gösterir
- **Manuel Yenileme:** "🔄 Şimdi Yenile" butonu ile güncel fiyatları tekrar çek

---

## ⚠️ Önemli Notlar

### yfinance Veri Kısıtlamaları
yfinance kütüphanesi BIST hisseleri için her zaman güncel veri sağlamayabilir. Bu durumda:
- Debug mode'u aç ve veri durumunu kontrol et
- Manuel yenileme yaparak tekrar dene
- Alternatif olarak production'da başka API'ler kullanılabilir (Twelve Data, Alpha Vantage)

Detaylı bilgi için [Walkthrough](./walkthrough.md) dosyasına bakın.

## 🔐 Güvenlik Notları

> ⚠️ **ÖNEMLİ:** `serviceAccountKey.json` dosyasını asla GitHub'a yüklemeyin!

> ⚠️ **NOT:** Bu bir MVP/demo uygulamadır. Production kullanımı için:
> - Şifre hash'leme ekleyin (bcrypt, argon2)
> - Firestore güvenlik kurallarını güncelleyin
> - HTTPS kullanın
> - Rate limiting ekleyin

## 🎯 Roadmap

- [ ] Grafik ve görselleştirme
- [ ] Portföy performans analizi
- [ ] Email bildirimleri
- [ ] Fiyat alarmları
- [ ] Mobil responsive tasarım iyileştirmesi
- [ ] Export (CSV, PDF)
- [ ] Alternatif veri kaynakları (Twelve Data, Alpha Vantage)
- [x] Cloud deployment hazırlığı (Streamlit Cloud)

## 🚀 Cloud Deployment

Uygulamayı Streamlit Cloud'a deploy etmek için [DEPLOYMENT.md](./DEPLOYMENT.md) dosyasına bakın.

## 📝 Lisans

MIT

---

Geliştirici: BIST Portfolio Team 📊
