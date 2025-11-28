#  İstanbul Kahve Dükkanları Konum Optimizasyonu

İstanbul'daki halk kütüphanelerinin konumlarını kullanarak, kahve dükkanları için **optimal lokasyonları** belirleyen bir veri bilimi projesi.

##  Proje Özeti

Bu proje, İstanbul Büyükşehir Belediyesi'nin (İBB) 60 halk kütüphanesi verisini kullanarak, kahve dükkanlarının en verimli konumlarını **matematiksel optimizasyon** ile hesaplar. Amaç, tüm kütüphanelere en kısa toplam mesafede hizmet verebilecek kahve dükkanı lokasyonlarını bulmaktır.

###  Temel Mantık

1. **Veri Kaynağı**: İBB'nin açık veri portalından kütüphane lokasyonları
2. **Optimizasyon**: Her kütüphaneye en yakın kahve dükkanını atayarak toplam mesafeyi minimize etme
3. **Görselleştirme**: Sonuçları interaktif harita üzerinde gösterme

---

## Proje Akışı

### Veri Toplama
- **Kaynak**: [İBB Açık Veri Portalı](https://data.ibb.gov.tr/dataset/ibb-kutuphaneleri-lokasyon-calisma-gun-ve-saatleri/resource/2ee4476c-9984-43de-96de-7aeda4da9aee)
- **İçerik**: 60 kütüphanenin adı, adresi, ilçesi, telefonu, çalışma saatleri

### Veri Ön İşleme (`pre-processing.ipynb`)
- **Geocoding**: Adreslerden enlem/boylam koordinatları çekme
- **API**: Photon API (OpenStreetMap tabanlı, ücretsiz)
- **Çıktı**: `adresler.json` (60 kütüphane + koordinatlar)

### Optimizasyon (`src/location_optimization.py`)
- **Algoritma**: Mixed Integer Linear Programming (MILP)
- **Kütüphane**: PuLP (CBC solver)
- **Amaç**: Toplam mesafeyi minimize eden (kuş uçuşu mesafesi) 5 kahve dükkanı konumu bulma

### Görselleştirme (`main.py`)
- **Harita**: Folium ile interaktif HTML haritası
- **Gösterim**:
  - Mor yıldız: Kahve dükkanı konumları
  - Mavi kitap: Kütüphaneler
  - Kırmızı çizgi: Kütüphane-kahve dükkanı bağlantıları

---

## Kurulum ve Çalıştırma

### Gereksinimler
```bash
Python 3.8+
```

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Programı Çalıştırın
```bash
python main.py
```

### 3. Sonucu Görüntüleyin
- Çıktı: `coffee_shop_map.html`
- Tarayıcınızda açın.

---

