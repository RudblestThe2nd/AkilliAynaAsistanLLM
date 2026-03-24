# Akilli Ayna AI Asistan

TÜBİTAK 2209-A kapsamında Fırat Üniversitesi'nde geliştirilen yapay zeka destekli akıllı ayna projesinin yazılım deposudur.

Danışman: Doç. Dr. Sinem Akyol
Koordinatör: Şevval Kaya
Geliştirici: Berkay Parçal
Geliştirici: Esra Kazan

---

# Proje Nedir?

Bu proje iki parçadan oluşur:

1. Telefon uygulaması (app klasörü): Görev ekleme, profil yönetimi ve sesli asistan arayüzü
2. Yapay zeka backend (backend klasörü): Sesli komutları anlayan ve yanıt üreten AI servisi

Kullanıcı telefon uygulamasındaki mikrofon butonuna basarak konuşur. Uygulama sesi metne çevirir, yapay zekaya gönderir ve yapay zekanın yanıtını sesli olarak okur.

---

# Klasör Yapısı

```
AkilliAynaAsistanLLM/
├── app/                  → Flutter mobil uygulaması
├── backend/              → Yapay zeka servisi
│   ├── main.py           → API sunucusu (bunu çalıştırırsınız)
│   ├── finetune_qwen3b.py → Modeli eğitmek için kullanılan script
│   ├── dataset.json      → Eğitim verisi
│   └── qwen3b-akilli-ayna/ → Eğitilmiş model adaptörü
└── README.md
```

---

# Gereksinimler

Bilgisayarınızda şunların kurulu olması gerekir:

- Python 3.11
- Anaconda veya Miniconda
- Flutter SDK (3.19 veya üzeri)
- NVIDIA ekran kartı (en az 8GB VRAM) --- sadece backend için
- Android telefon (uygulamayı test etmek için)

---

# Kurulum Adımları

## 1. Depoyu İndirin

```bash
git clone https://github.com/RudblestThe2nd/AkilliAynaAsistanLLM.git
cd AkilliAynaAsistanLLM
```

## 2. Base Modeli İndirin

Yapay zeka modelinin temel dosyaları GitHub'da değil, Hugging Face'de bulunuyor. Çok büyük olduğu için buraya koymak mümkün değildi.

Önce Python ortamınızı hazırlayın:

```bash
conda create -n TubitakLLM python=3.11
conda activate TubitakLLM
pip install torch transformers peft trl datasets fastapi uvicorn
```

Sonra modeli indirin:

```bash
cd backend
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Qwen/Qwen2.5-3B-Instruct',
    local_dir='./qwen3b-base',
)
"
```

Bu işlem internet hızınıza göre 20-60 dakika sürebilir, yaklaşık 6GB indirilecek.

## 3. Backend'i Çalıştırın

```bash
conda activate TubitakLLM
cd backend
python main.py
```

Ekranda "Model hazır!" yazısını gördükten sonra backend çalışıyor demektir. Bu terminali kapatmayın.

## 4. Flutter Uygulamasını Telefona Yükleyin

Telefonu USB ile bilgisayara bağlayın. Telefonunuzda "Geliştirici Seçenekleri" menüsünden "USB Hata Ayıklama" seçeneğini açın.

Yeni bir terminal açın ve şunu çalıştırın:

```bash
cd app
flutter pub get
flutter run
```

Uygulama otomatik olarak telefona yüklenecek ve açılacaktır.

---

# Uygulamayı Kullanmak

1. Uygulamayı açın
2. İlk açılışta profil oluşturun (isim ve PIN girin)
3. Görevler sekmesinden görev ekleyin
4. Ana sayfadaki mikrofon butonuna basın ve konuşun

Konuşabileceğiniz örnek komutlar:

- "Bugün ne yapacağım"
- "Yarın programım ne"
- "Bu hafta ne var"
- "Sabah planım nedir"
- "Görev ekle yarın saat 10 toplantı"
- "Hatırlat akşam ilaç al"

---

# Sık Sorulan Sorular

Backend çalışıyor ama uygulama bağlanamıyor:
Telefon ve bilgisayar aynı WiFi ağında olmalıdır. backend/main.py dosyasında IP adresini kendi bilgisayarınızın IP'si ile değiştirin. app/lib/core/constants/api_constants.dart dosyasında da aynı IP'yi güncelleyin.

Model indirme hatası alıyorum:
Hugging Face hesabı açıp giriş yapmanız gerekiyor olabilir. Şu komutu çalıştırın ve token girin:
python -c "from huggingface_hub import login; login()"

Uygulama telefonda açılmıyor:
USB Hata Ayıklama açık olduğundan emin olun. Telefon ekranı kilitliyken bağlamayın.

---

# Teknik Bilgiler

Model: Qwen2.5-3B-Instruct (QLoRA fine-tuned)
Eğitim verisi: 3350 Türkçe örnek
Backend: FastAPI + NGINX (TLS)
Mobil: Flutter (Android)
Veritabanı: SQLite

---

Fırat Üniversitesi - TÜBİTAK 2209-A - 2025-2026
