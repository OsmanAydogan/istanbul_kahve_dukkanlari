# Kahve Dükkanı Konum Optimizasyonu - Müşteri Sunumu

Bu belge, uygulamanın ne yaptığını, hangi teknolojileri kullandığını ve sonuçların neden **matematiksel olarak garanti altında** olduğunu açıklamak için hazırlanmıştır.

---

## 1. Bu Uygulama Nedir?

Bu uygulama, bir işletme sahibinin şu sorusuna bilimsel cevap verir:

> "Elimde 10 tane potansiyel dükkan yeri var. 3 tane dükkan açmak istiyorum. Hangi 3'ünü seçmeliyim ki, tüm müşterilerime (kütüphaneler, okullar, meydanlar vb.) en kısa toplam mesafede ulaşabileyim?"

Bu problem, elle veya sezgiyle çözülemeyecek kadar karmaşıktır. 10 adaydan 3'ünü seçmenin **120 farklı kombinasyonu** vardır. 20 adaydan 5'ini seçmenin ise **15.504 kombinasyonu** vardır. Uygulama, tüm bu ihtimalleri kısa sürede değerlendirip **en iyi olanı** bulur.

---

## 2. Hangi Teknolojileri Kullanıyor?

| Teknoloji | Görevi | Güvenilirlik |
|---|---|---|
| **Google Maps Distance Matrix API** | İki nokta arasındaki **gerçek yol mesafesini** (tek yönlü sokaklar, 'U' dönüşleri, köprüler dahil) hesaplar. Kuş uçuşu değil, gerçek yol ağındaki km. | Dünya standartı. Uber, taksi uygulamaları aynısını kullanır. |
| **PuLP (Python Kütüphanesi)** | Matematiksel optimizasyon modeli kurar. | Açık kaynak, akademik çalışmalarda ve endüstride yaygın kullanılır. |
| **CBC Solver (Coin-or Branch and Cut)** | Modeli çözer ve **en iyi sonucu garanti eder**. | Doğrusal ve tamsayılı programlama için dünya çapında kabul görmüş, ücretsiz ve profesyonel bir çözücüdür. |

---

## 3. Bu Sonuç Gerçekten En İyisi mi? Garantisi Nedir?

**Evet, matematiksel olarak kanıtlanmış "en iyi" sonuçtur.**

Bu uygulama, akademik literatürde **"p-Median Problemi"** olarak bilinen klasik bir optimizasyon problemini çözer. Bu problem 1960'lardan beri çalışılmaktadır ve çözümü ispatlanmıştır.

### Algoritmanın Çalışma Prensibi: Branch and Bound

Kullanılan CBC çözücüsü, **"Dal ve Sınır" (Branch and Bound)** algoritmasını kullanır. Bu algoritma:

1.  Tüm olası kombinasyonları bir ağaç gibi dallandırır.
2.  Her dalın potansiyel sonucunu hesaplar ve bir "alt sınır" belirler.
3.  Eğer bir dalın alt sınırı, şu ana kadar bulunan en iyi sonuçtan kötüyse, o dalı tamamen keser (budama).
4.  Sonunda, kesilmemiş tek bir dal kalır ve bu **kesin olarak global optimum**dur.

### Matematiksel Garanti

Çözücü şu mesajı verir: **"Optimal Solution Found"**. Bu, şu anlama gelir:

> "Başka hiçbir kombinasyon, bu kombinasyondan daha iyi bir toplam mesafe veremez."

Bu, tahmin veya yaklaşık değildir. **Kesin matematiksel ispatla** kanıtlanmış sonuçtur.

---

## 4. Gerçekten En Yakın Noktalar mı Seçildi?

**Evet.** Algoritmanın kurallarından biri şudur:

> "Her müşteri, kendisine en yakın **açık** dükkana atanmalıdır."

Eğer 3 dükkan açıldıysa:
*   Her müşteri, bu 3 dükkandan kendisine en yakın olana bağlanır.
*   Toplam mesafe, bu 3 dükkanın seçimiyle mümkün olan **en düşük değerdir**.

Yani sadece "iyi" değil, matematiksel olarak **"mümkün olan en iyi"** sonuçtur.

> **Önemli Not:** Model, seçilen dükkanların kapasitesinin (m² veya personel sayısı), yönlendirilen tüm müşterileri ağırlayabileceği varsayımıyla (Sınırsız Kapasite Modeli) çalışır.


---

## 5. Mesafeler Doğru mu?

Uygulama, **kuş uçuşu mesafe kullanmaz**. Google Maps Distance Matrix API ile:
*   Gerçek sokak yolları
*   Tek yönlü caddeler
*   Köprüler, tüneller
*   Araca göre en kısa rota

hesaplanır. Yani sonuçlar **gerçek dünya koşullarına** uygundur.

---

## 6. Özet

| Soru | Cevap |
|---|---|
| Bu uygulama ne yapıyor? | Belirli sayıda dükkanın, müşterilere en yakın olacak şekilde nereye açılacağını buluyor. |
| Sonuç güvenilir mi? | Evet. Matematiksel optimizasyon ile **kesin en iyi sonuç** garanti altındadır. |
| Mesafeler gerçek mi? | Evet. Google Maps ile gerçek yol mesafeleri kullanılıyor. |
| Bu bir tahmin mi? | Hayır. Bu, **Branch and Bound** algoritmasıyla kanıtlanmış global optimumdur. |
| Kanıtı var mı? | p-Median problemi 1960'lardan beri çalışılmaktadır. Algoritmalar akademik olarak doğrulanmıştır. |

---

## 7. Akademik Referanslar

Müşteriniz daha fazla bilgi isterse:
*   **Hakimi (1964):** p-Median probleminin temel teoremi.
*   **Branch and Bound Algoritması:** [Wikipedia](https://en.wikipedia.org/wiki/Branch_and_bound)
*   **PuLP Kütüphanesi:** [coin-or.github.io/pulp](https://coin-or.github.io/pulp/)
*   **Google Distance Matrix API:** [developers.google.com](https://developers.google.com/maps/documentation/distance-matrix)
