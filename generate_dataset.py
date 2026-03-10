import json
import random

# Temel 50 örnek
base_data = [
    {"instruction": "Bugün programımda ne var?", "input": "Tarih: Pazartesi. Plan: 10:00 ekip toplantısı, 14:00 spor, 19:00 arkadaş buluşması.", "output": "Bugün saat 10:00'da ekip toplantın, 14:00'te spor ve 19:00'da arkadaşlarınla buluşman var."},
    {"instruction": "Bugün önemli bir toplantım var mı?", "input": "Takvim: 11:30 müşteri toplantısı.", "output": "Evet. Saat 11:30'da müşteri toplantın bulunuyor."},
    {"instruction": "Akşam planım neydi?", "input": "Takvim: 20:00 arkadaşlarla yemek.", "output": "Akşam saat 20:00'de arkadaşlarınla yemek planın var."},
    {"instruction": "Bugün spor yapacak mıydım?", "input": "Plan: 18:30 fitness.", "output": "Evet. Saat 18:30'da fitness antrenmanı planlamışsın."},
    {"instruction": "Bugün yapmam gereken görevler neler?", "input": "Todo: proje raporu bitir, market alışverişi.", "output": "Bugün proje raporunu tamamlaman ve market alışverişi yapman gerekiyor."},
    {"instruction": "Öğleden sonra planım ne?", "input": "Plan: 13:00 rapor yazımı, 16:00 müşteri araması.", "output": "Öğleden sonra saat 13:00'te rapor yazımı ve 16:00'da müşteri araması planın var."},
    {"instruction": "Sabah bir randevum var mı?", "input": "Takvim: 08:30 doktor randevusu.", "output": "Evet. Sabah saat 08:30'da doktor randevun bulunuyor."},
    {"instruction": "Bugün boş vaktim var mı?", "input": "Takvim: 09:00 ders, 12:00 yemek, 17:00 toplantı.", "output": "Öğle yemeğinden sonra saat 17:00'ye kadar boş zamanın var."},
    {"instruction": "Bugün için önerin var mı?", "input": "Takvim: yoğun program.", "output": "Bugün programın yoğun görünüyor. Boşluklarda kısa yürüyüş yapmayı veya biraz dinlenmeyi düşünebilirsin."},
    {"instruction": "Bugün en önemli görevim ne?", "input": "Görev: proje teslimi.", "output": "Bugün en önemli görevin proje teslimini tamamlamak."},
    {"instruction": "Toplantımdan önce bana hatırlatma yap.", "input": "Toplantı: 14:00 ekip toplantısı.", "output": "Tamam. Saat 13:50'de toplantın için hatırlatma yapacağım."},
    {"instruction": "Akşam spor yapmayı unutursam hatırlat.", "input": "Plan: 19:00 koşu.", "output": "Saat 18:45'te koşu planın için sana hatırlatma göndereceğim."},
    {"instruction": "Bugün hava durumuna göre önerin var mı?", "input": "Hava: yağmurlu.", "output": "Bugün yağmur bekleniyor. Dışarı çıkarken şemsiye almanı öneririm."},
    {"instruction": "Yarın sabah erken kalkmam gerekiyor mu?", "input": "Takvim: 07:30 uçuş.", "output": "Evet. Yarın saat 07:30'da uçuşun var, erken kalkman gerekiyor."},
    {"instruction": "Bugün kendime ayıracak zamanım var mı?", "input": "Takvim: 09:00 toplantı, 13:00 rapor, 17:00 spor.", "output": "Öğleden sonra spor öncesinde kısa bir boş zamanın bulunuyor."},
    {"instruction": "Bugün kaç toplantım var?", "input": "Takvim: 10:00 ekip toplantısı, 16:00 proje toplantısı.", "output": "Bugün iki toplantın var: 10:00 ve 16:00."},
    {"instruction": "Bugünkü ilk görevim ne?", "input": "Plan: 09:00 rapor hazırlama.", "output": "Bugünkü ilk görevin saat 09:00'da rapor hazırlamak."},
    {"instruction": "Bugün dışarı çıkmam gerekiyor mu?", "input": "Plan: 15:00 banka işlemi.", "output": "Evet. Saat 15:00'te banka işlemi için dışarı çıkman gerekiyor."},
    {"instruction": "Bugün yapılacaklar listemde ne var?", "input": "Todo: sunum hazırla, e-posta gönder.", "output": "Bugün sunum hazırlaman ve bazı e-postaları göndermen gerekiyor."},
    {"instruction": "Bugün çok yoğun muyum?", "input": "Takvim: 09:00 toplantı, 11:00 toplantı, 14:00 toplantı.", "output": "Evet. Bugün üç toplantın var ve programın oldukça yoğun."},
    {"instruction": "Bugün dersim var mı?", "input": "Takvim: 13:00 yapay zeka dersi.", "output": "Evet. Saat 13:00'te yapay zeka dersin var."},
    {"instruction": "Bugün alışveriş yapmam gerekiyor mu?", "input": "Todo: market alışverişi.", "output": "Evet. Bugün market alışverişi yapman gerekiyor."},
    {"instruction": "Akşam planım boş mu?", "input": "Takvim: akşam için plan yok.", "output": "Evet. Akşam saatleri için planlanmış bir etkinliğin görünmüyor."},
    {"instruction": "Bugün yürüyüş planlamış mıydım?", "input": "Plan: 18:00 yürüyüş.", "output": "Evet. Saat 18:00'de yürüyüş planlamışsın."},
    {"instruction": "Bugün hangi görevlerimi tamamlamalıyım?", "input": "Todo: rapor yaz, e-posta gönder.", "output": "Bugün rapor yazman ve e-postaları göndermen gerekiyor."},
    {"instruction": "Öğle arasında planım var mı?", "input": "Takvim: 12:30 öğle yemeği.", "output": "Evet. Saat 12:30'da öğle yemeği planın var."},
    {"instruction": "Bugün kendime mola vermeli miyim?", "input": "Takvim: yoğun.", "output": "Programın yoğun görünüyor. Kısa molalar vermen faydalı olabilir."},
    {"instruction": "Bugün çalışmam gereken bir proje var mı?", "input": "Todo: proje geliştirme.", "output": "Evet. Bugün proje geliştirme üzerinde çalışman gerekiyor."},
    {"instruction": "Bugün telefon görüşmem var mı?", "input": "Takvim: 15:00 müşteri araması.", "output": "Evet. Saat 15:00'te müşteriyle telefon görüşmen var."},
    {"instruction": "Bugün erken yatmam gerekiyor mu?", "input": "Takvim: yarın 06:00 alarm.", "output": "Evet. Yarın erken kalkman gerektiği için bu akşam erken yatman iyi olabilir."},
    {"instruction": "Bugün kendimi geliştirmek için bir şey yapmalı mıyım?", "input": "Boş zaman: 1 saat.", "output": "Bugün yaklaşık bir saat boş zamanın var. Bu zamanı öğrenme veya okuma için değerlendirebilirsin."},
    {"instruction": "Bugün hangi saatte spor var?", "input": "Plan: 19:00 spor salonu.", "output": "Bugün spor salonu planın saat 19:00'da."},
    {"instruction": "Bugün bir sunumum var mı?", "input": "Takvim: 11:00 sunum.", "output": "Evet. Saat 11:00'de bir sunumun var."},
    {"instruction": "Bugün arkadaşlarımla buluşacak mıyım?", "input": "Takvim: 20:30 arkadaş buluşması.", "output": "Evet. Saat 20:30'da arkadaşlarınla buluşma planın var."},
    {"instruction": "Bugün dinlenmek için zamanım var mı?", "input": "Takvim: öğleden sonra boşluk.", "output": "Evet. Öğleden sonra dinlenmek için biraz boş zamanın var."},
    {"instruction": "Bugün hangi işi önce yapmalıyım?", "input": "Todo: rapor, sunum.", "output": "Öncelikle raporunu tamamlaman daha önemli görünüyor."},
    {"instruction": "Bugün ders çalışmam gerekiyor mu?", "input": "Todo: sınav hazırlığı.", "output": "Evet. Bugün sınav hazırlığı için ders çalışman gerekiyor."},
    {"instruction": "Bugün yürüyüş için uygun zamanım var mı?", "input": "Takvim: 17:00 sonrası boş.", "output": "Evet. Saat 17:00'den sonra yürüyüş için uygun zamanın var."},
    {"instruction": "Bugün neyi unutmamam gerekiyor?", "input": "Görev: proje teslimi.", "output": "Bugün proje teslimini unutmaman gerekiyor."},
    {"instruction": "Bugün yapılacak ilk toplantı ne zaman?", "input": "Takvim: 09:30 toplantı.", "output": "Bugünkü ilk toplantın saat 09:30'da."},
    {"instruction": "Bugün işten sonra planım var mı?", "input": "Takvim: 19:30 yemek.", "output": "Evet. İşten sonra saat 19:30'da yemek planın var."},
    {"instruction": "Bugün hangi saatlerde boşum?", "input": "Takvim: 09:00 ve 14:00 toplantı.", "output": "Toplantılar dışında kalan saatlerde boş zamanın bulunuyor."},
    {"instruction": "Bugün kendime hedef koymalı mıyım?", "input": "Boş gün.", "output": "Bugün daha verimli olmak için küçük bir hedef belirleyebilirsin."},
    {"instruction": "Bugün yapmam gereken en zor iş ne?", "input": "Görev: proje raporu.", "output": "Bugün en zor görevin proje raporunu tamamlamak olabilir."},
    {"instruction": "Bugün akşam kaçta boş olacağım?", "input": "Takvim: 18:00 spor.", "output": "Spor sonrası akşam saatlerinde boş olacaksın."},
    {"instruction": "Bugün kendime zaman ayırabilir miyim?", "input": "Takvim: öğleden sonra boşluk.", "output": "Evet. Öğleden sonra kendine zaman ayırabileceğin bir boşluk bulunuyor."},
    {"instruction": "Bugün yapılacak son planım ne?", "input": "Takvim: 21:00 film.", "output": "Bugünün son planı saat 21:00'de film izlemek."},
    {"instruction": "Bugün erken çıkmam gereken bir yer var mı?", "input": "Takvim: 17:30 randevu.", "output": "Evet. Saat 17:30'da bir randevun var."},
    {"instruction": "Bugün telefonla aramam gereken biri var mı?", "input": "Todo: müşteri araması.", "output": "Evet. Bugün müşteriyi araman gerekiyor."},
    {"instruction": "Bugün dışarı çıkmak için uygun zamanım var mı?", "input": "Takvim: öğleden sonra boş.", "output": "Öğleden sonra dışarı çıkmak için uygun zamanın var."},
    {"instruction": "Bugün neyi tamamlamam gerekiyor?", "input": "Todo: rapor teslimi.", "output": "Bugün rapor teslimini tamamlaman gerekiyor."},
]

# Varyasyon üreticiler
saat_degiskenler = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                    "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
                    "20:00", "20:30", "21:00"]

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

toplanti_turleri = [
    "ekip toplantısı", "müşteri toplantısı", "proje toplantısı",
    "yönetim toplantısı", "haftalık toplantı", "strateji toplantısı",
    "değerlendirme toplantısı", "planlama toplantısı"
]

spor_turleri = [
    "fitness", "koşu", "yüzme", "yoga", "pilates", "bisiklet",
    "basketbol", "futbol", "tenis", "spor salonu"
]

gorev_turleri = [
    "proje raporu", "sunum hazırlığı", "kod geliştirme", "e-posta yazışması",
    "araştırma", "belge hazırlama", "toplantı notu", "haftalık rapor",
    "müşteri takibi", "sınav hazırlığı", "ödev teslimi", "makale yazımı"
]

kullanici_adlari = ["Berkay", "Şevval", "Esra", "Ali", "Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak"]

# Yeni varyasyon örnekleri üret
def varyasyon_uret():
    yeni_ornekler = []

    # 1. Toplantı varyasyonları
    for _ in range(80):
        saat = random.choice(saat_degiskenler)
        toplanti = random.choice(toplanti_turleri)
        gun = random.choice(gunler)
        onceki_saat = saat_degiskenler[max(0, saat_degiskenler.index(saat)-1)]

        yeni_ornekler.append({
            "instruction": random.choice([
                f"Bugün {toplanti}m var mı?",
                f"{gun} günü toplantım kaçta?",
                "Yaklaşan toplantım ne zaman?",
                "Toplantımı hatırlatır mısın?",
            ]),
            "input": f"Takvim: {saat} {toplanti}.",
            "output": random.choice([
                f"Evet. Saat {saat}'de {toplanti}n bulunuyor.",
                f"Bugün saat {saat}'de {toplanti}n var.",
                f"Saat {onceki_saat}'de {toplanti}n için hazırlanmaya başlamalısın, toplantı {saat}'de.",
            ])
        })

    # 2. Spor varyasyonları
    for _ in range(80):
        saat = random.choice(saat_degiskenler[10:])  # öğleden sonra
        spor = random.choice(spor_turleri)
        onceki_saat = saat_degiskenler[max(0, saat_degiskenler.index(saat)-1)]

        yeni_ornekler.append({
            "instruction": random.choice([
                f"Bugün {spor} planım var mı?",
                "Spor saatimi hatırlatır mısın?",
                f"{spor} yapmayı unutursam hatırlat.",
                "Bugün spor var mı?",
            ]),
            "input": f"Plan: {saat} {spor}.",
            "output": random.choice([
                f"Evet. Saat {saat}'de {spor} planın var.",
                f"Saat {onceki_saat}'de {spor} için hazırlanmaya başlamalısın.",
                f"Bugün {spor} planın saat {saat}'de.",
            ])
        })

    # 3. Görev varyasyonları
    for _ in range(80):
        gorev = random.choice(gorev_turleri)
        gorev2 = random.choice(gorev_turleri)
        while gorev2 == gorev:
            gorev2 = random.choice(gorev_turleri)

        yeni_ornekler.append({
            "instruction": random.choice([
                "Bugün hangi görevleri tamamlamalıyım?",
                "Yapılacaklar listemde ne var?",
                "Bugün neyi bitirmem gerekiyor?",
                "En önemli görevim ne?",
            ]),
            "input": f"Todo: {gorev}, {gorev2}.",
            "output": random.choice([
                f"Bugün {gorev} ve {gorev2} görevlerini tamamlaman gerekiyor.",
                f"Öncelikle {gorev} üzerinde çalışmanı, ardından {gorev2}yi tamamlamanı öneririm.",
                f"Bugünkü görevlerin: {gorev} ve {gorev2}.",
            ])
        })

    # 4. Yoğun program varyasyonları
    for _ in range(60):
        s1 = random.choice(saat_degiskenler[:10])
        s2 = random.choice(saat_degiskenler[10:16])
        s3 = random.choice(saat_degiskenler[16:])
        t1 = random.choice(toplanti_turleri)
        t2 = random.choice(toplanti_turleri)
        t3 = random.choice(spor_turleri)

        yeni_ornekler.append({
            "instruction": random.choice([
                "Bugün çok yoğun muyum?",
                "Bugünkü programım nasıl?",
                "Bugün boş zamanım var mı?",
                "Bugün ne kadar meşgulüm?",
            ]),
            "input": f"Takvim: {s1} {t1}, {s2} {t2}, {s3} {t3}.",
            "output": random.choice([
                f"Bugün {s1}, {s2} ve {s3} olmak üzere üç planın var. Programın oldukça yoğun.",
                f"Programın dolu görünüyor: {s1} {t1}, {s2} {t2} ve {s3} {t3}.",
                f"Bugün yoğun bir günün var. Molalar vermeyi unutma.",
            ])
        })

    # 5. Kişiselleştirilmiş varyasyonlar
    for _ in range(60):
        ad = random.choice(kullanici_adlari)
        saat = random.choice(saat_degiskenler)
        etkinlik = random.choice(toplanti_turleri + spor_turleri + gorev_turleri)

        yeni_ornekler.append({
            "instruction": f"Bugünkü programımı söyler misin?",
            "input": f"Kullanıcı: {ad}. Plan: {saat} {etkinlik}.",
            "output": f"{ad}, bugün saat {saat}'de {etkinlik} planın bulunuyor.",
        })

    # 6. Hatırlatıcı varyasyonları
    for _ in range(60):
        saat = random.choice(saat_degiskenler[8:])
        onceki_saat = saat_degiskenler[max(0, saat_degiskenler.index(saat)-1)]
        etkinlik = random.choice(toplanti_turleri + spor_turleri)

        yeni_ornekler.append({
            "instruction": random.choice([
                f"{etkinlik} için beni hatırlat.",
                f"{saat} öncesinde uyarır mısın?",
                "Planım başlamadan önce hatırlat.",
            ]),
            "input": f"Plan: {saat} {etkinlik}.",
            "output": f"Saat {onceki_saat}'de {etkinlik} için sana hatırlatma yapacağım.",
        })

    # 7. Öneri varyasyonları
    for _ in range(60):
        yeni_ornekler.append({
            "instruction": random.choice([
                "Bugün kendimi nasıl motive edebilirim?",
                "Daha verimli olmak için ne yapmalıyım?",
                "Bugün için bir önerin var mı?",
                "Nasıl daha iyi bir gün geçirebilirim?",
            ]),
            "input": random.choice([
                "Boş gün.", "Yoğun program.", "Orta yoğunlukta gün.", "Boş zaman: 2 saat."
            ]),
            "output": random.choice([
                "Küçük hedefler belirleyerek güne başlamak motivasyonunu artırabilir.",
                "Pomodoro tekniğiyle çalışmayı deneyebilirsin: 25 dakika çalış, 5 dakika mola ver.",
                "Önce zor görevleri tamamlamak gün içinde daha rahat hissettirer.",
                "Kısa yürüyüşler zihnini tazeleyebilir ve verimliliğini artırabilir.",
                "Günün başında en önemli 3 görevi belirlemek odaklanmanı kolaylaştırır.",
            ])
        })

    return yeni_ornekler

# Dataset oluştur
varyasyonlar = varyasyon_uret()
tam_dataset = base_data + varyasyonlar
random.shuffle(tam_dataset)

# Alpaca formatında kaydet
with open("dataset.json", "w", encoding="utf-8") as f:
    json.dump(tam_dataset, f, ensure_ascii=False, indent=2)

# JSONL formatında da kaydet (bazı trainer'lar bunu ister)
with open("dataset.jsonl", "w", encoding="utf-8") as f:
    for item in tam_dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ Dataset oluşturuldu!")
print(f"📊 Toplam örnek sayısı: {len(tam_dataset)}")
print(f"📁 Dosyalar: dataset.json, dataset.jsonl")

# İlk 3 örneği göster
print("\n--- İlk 3 örnek ---")
for i, item in enumerate(tam_dataset[:3]):
    print(f"\n[{i+1}]")
    print(f"  Instruction: {item['instruction']}")
    print(f"  Input: {item['input']}")
    print(f"  Output: {item['output']}")
