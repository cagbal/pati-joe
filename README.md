
# Kod Yazmayı Bıraktım! - Gemini ile Websitesi

Bu proje, Çağatay Odabaşı'nın **"Kod Yazmayı Bıraktım! ✋ (Google Gemini Her Şeyi Yaptı)"** başlıklı YouTube videosunda, tamamen Google Gemini yapay zeka asistanı kullanılarak oluşturulmuştur.

🎥 **Video Bağlantısı:** [İzlemek için tıklayın](https://www.youtube.com/watch?v=LxTv2nQZgBA)

## ⚠️ ÖNEMLİ UYARI ⚠️

**Bu depodaki tüm kodlar %100 Yapay Zeka (Google Gemini) tarafından oluşturulmuştur.**

Lütfen kodu kullanırken veya incelerken aşağıdakileri göz önünde bulundurun:
*   Bu kod, deneysel amaçlarla ve yapay zeka yeteneklerini göstermek için üretilmiştir.
*   Güvenlik, performans veya yazılım geliştirme "best practice" (en iyi uygulama) standartlarını tam olarak karşılamayabilir.
*   Prodüksiyon (canlı) ortamlarında kullanmadan önce mutlaka kodu dikkatlice inceleyin, test edin ve gerekli optimizasyonları yapın.

## Proje Hakkında
Bu proje, yapay zeka destekli kodlamanın sınırlarını zorlamak ve tek satır bile elle kod yazmadan, sadece yönlendirmelerle (prompting) sıfırdan bir web sitesi oluşturma sürecini belgelemek amacıyla hazırlanmıştır.

---
*Bu README dosyası Antigravity asistanı tarafından otomatik olarak oluşturulmuştur.*

## 🚀 Nasıl Çalıştırılır?

Bu projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

### Gereksinimler
Python 3.8 veya üzeri bir sürümün yüklü olması gerekmektedir.

### Kurulum

Bu proje, hızlı paket yönetimi için **uv** kullanır.

1.  Uygulama ortamını hazırlayın:
    ```bash
    uv venv
    source .venv/bin/activate  # Windows için: .venv\Scripts\activate
    uv pip install fastapi uvicorn sqlalchemy jinja2 python-multipart bcrypt "python-jose[cryptography]"
    ```

### Çalıştırma

1.  Uygulamayı başlatın:
    ```bash
    uv run main.py
    ```
    *Alternatif olarak:* `uv run uvicorn main:app --reload`

2.  Tarayıcınızda şu adrese gidin:
    [http://localhost:8000](http://localhost:8000)

### Demo Hesap Bilgileri
Uygulama başladığında otomatik olarak demo verileri oluşturulur.
*   **Kullanıcı Adı:** `demo`
*   **Şifre:** `demo123`

