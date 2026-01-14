# BIST Portfolio SaaS - Cloud Deployment Guide

## 🚀 Streamlit Cloud'a Deploy Etme

Streamlit Cloud ücretsiz ve çok kolay! Şu adımları takip et:

### 1. GitHub Repository Oluştur

```bash
cd /Users/tunahangokgoz/Desktop/borsacım
git init
git add .
git commit -m "Initial commit - BIST Portfolio SaaS"
```

GitHub'da yeni repository oluştur ve push et:
```bash
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/bist-portfolio.git
git push -u origin main
```

> **ÖNEMLİ:** `.gitignore` dosyası `serviceAccountKey.json` dosyasını hariç tutacak - bu çok önemli!

### 2. Streamlit Cloud'a Kayıt Ol

1. [share.streamlit.io](https://share.streamlit.io) adresine git
2. GitHub hesabınla giriş yap
3. Repository'ni bağla

### 3. Firebase Secrets'ı Ekle

Streamlit Cloud dashboard'da:

1. App Settings → Secrets'a git
2. `serviceAccountKey.json` dosyasının içeriğini TOML formatında ekle:

```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR-KEY-HERE\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
```

### 4. Firestore Client'ı Güncelle

`src/db/firestore_client.py` dosyasına cloud mode ekleyelim:

```python
def _initialize_firebase(self):
    """Firebase Admin SDK'yı başlat"""
    try:
        firebase_admin.get_app()
    except ValueError:
        # Streamlit Cloud check
        if 'firebase' in st.secrets:
            # Cloud mode - secrets.toml kullan
            cred = credentials.Certificate(dict(st.secrets['firebase']))
        else:
            # Local mode - JSON dosyası kullan
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Firebase credentials not found")
            cred = credentials.Certificate(cred_path)
        
        firebase_admin.initialize_app(cred)
    
    self._client = firestore.client()
```

### 5. Deploy Et!

1. Streamlit Cloud dashboard'da "Deploy" butonuna tıkla
2. Repository, branch (main) ve main file (app.py) seç
3. Deploy! ⚡

App birkaç dakika içinde hazır olacak: `https://your-app.streamlit.app`

---

## 🔧 Alternatif: Diğer Cloud Platformlar

### Heroku
- Ücretsiz seviye kaldırıldı, ama hobi projeler için uygun fiyatlı
- `Procfile` gerekiyor

### Railway
- Ücretsiz $5 / ay kredi
- Otomatik deployment

### Google Cloud Run
- Serverless
- Sadece kullandığın kadar öde

---

## ⚡ Optimizasyonlar

### Performans
- Cache sürelerini ayarla (şu an 60 saniye)
- Database connection pooling
- CDN kullanımı

### Güvenlik
- Firebase güvenlik kurallarını production'a al
- HTTPS zorunlu (Streamlit Cloud otomatik sağlıyor)
- Rate limiting ekle

---

## 🐛 Troubleshooting

**yfinance BIST verileri çekemiyor:**
- yfinance bazen BIST için güvenilir değil
- Alternative API'ler:
  - Investing.com API
  - Alpha Vantage (ücretsiz tier var)
  - Twelve Data

**Deployment hatası:**
- Secrets doğru formatta mı kontrol et
- requirements.txt tüm paketleri içeriyor mu
- Logs'u kontrol et

---

## 📝 Post-Deployment Checklist

- [ ] Test kullanıcısı oluştur
- [ ] Portföy oluştur ve işlem ekle
- [ ] Fiyat verilerini kontrol et
- [ ] Mobile responsive kontrolü
- [ ] Performance testi
- [ ] Gerçek kullanıcılara test ettir
