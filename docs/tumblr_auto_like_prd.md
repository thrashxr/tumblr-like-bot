# Tumblr Otomatik Beğeni Otomasyonu PRD

## 1. Ürün Tanımı

### 1.1 Amaç

Bu otomasyon aracı, Tumblr platformunda belirlenen kriterlere göre otomatik olarak içerikleri beğenme işlemini gerçekleştirecektir. Kullanıcıların etkileşimini artırmak ve zaman tasarrufu sağlamak amacıyla geliştirilecektir.

### 1.2 Hedef Kitle

-  Tumblr içerik üreticileri
-  Sosyal medya yöneticileri
-  Tumblr topluluk yöneticileri

## 2. Teknik Gereksinimler

### 2.1 Sistem Gereksinimleri

-  Python 3.8 veya üzeri
-  İnternet bağlantısı
-  Tumblr API erişimi
-  OAuth kimlik doğrulama bilgileri

### 2.2 API Gereksinimleri

-  Tumblr API v2 desteği
-  OAuth2 kimlik doğrulama
-  API istek limitleri gözetimi (Saatte 300 istek, günde 5,000 istek)
-  Günlük beğeni limiti (1,000 beğeni/gün)

## 3. Fonksiyonel Özellikler

### 3.1 Temel Özellikler

-  Otomatik giriş ve kimlik doğrulama
-  Hedef blog/etiket bazlı beğeni
-  Beğeni limiti kontrolü
-  Otomatik duraklama ve devam etme
-  Hata yönetimi ve loglama

### 3.2 Beğeni Kriterleri

-  Etiket bazlı filtreleme
-  Blog bazlı filtreleme
-  İçerik türü filtreleme (metin, fotoğraf, video vb.)
-  Tarih bazlı filtreleme

### 3.3 Güvenlik Özellikleri

-  API anahtar yönetimi
-  Oturum güvenliği
-  Rate limiting kontrolü
-  IP ban koruması

## 4. Kullanıcı Arayüzü

### 4.1 Yapılandırma Dosyası

```yaml
api_credentials:
   consumer_key: ''
   consumer_secret: ''
   oauth_token: ''
   oauth_secret: ''

like_settings:
   max_likes_per_hour: 200
   max_likes_per_day: 1000
   tags: ['sanat', 'teknoloji', 'bilim']
   blog_blacklist: []
   content_types: ['photo', 'text']
   min_notes: 5

timing:
   delay_between_likes: 30
   rest_time: 3600
   start_time: '09:00'
   end_time: '23:00'
```

### 4.2 Log Formatı

```log
[TARIH SAAT] [SEVIYE] - Mesaj
2024-02-09 14:30:15 [INFO] - Program başlatıldı
2024-02-09 14:30:16 [INFO] - API bağlantısı başarılı
2024-02-09 14:30:20 [INFO] - Gönderi beğenildi: POST_ID
```

## 5. Güvenlik ve Uyumluluk

### 5.1 Veri Güvenliği

-  Hassas bilgilerin şifrelenmesi
-  API anahtarlarının güvenli depolanması
-  Oturum verilerinin güvenli yönetimi

### 5.2 Platform Uyumluluğu

-  Tumblr Topluluk Kurallarına uygunluk
-  API kullanım politikalarına uygunluk
-  Rate limiting kurallarına uygunluk

## 6. Hata Yönetimi

### 6.1 Hata Senaryoları

-  API bağlantı hataları
-  Rate limiting aşımı
-  Kimlik doğrulama hataları
-  Ağ bağlantı sorunları

### 6.2 Kurtarma Mekanizmaları

-  Otomatik yeniden deneme
-  Akıllı bekleme süreleri
-  Oturum yenileme
-  Hata bildirimleri

## 7. Performans Metrikleri

### 7.1 İzlenecek Metrikler

-  Başarılı beğeni sayısı
-  Hata oranları
-  API yanıt süreleri
-  Çalışma süresi istatistikleri

### 7.2 Raporlama

-  Günlük aktivite raporu
-  Hata log raporu
-  Performans istatistikleri
-  Beğeni analizi

## 8. Geliştirme Yol Haritası

### 8.1 Faz 1 - Temel Özellikler

-  API entegrasyonu
-  Temel beğeni fonksiyonu
-  Basit konfigürasyon
-  Temel hata yönetimi

### 8.2 Faz 2 - Gelişmiş Özellikler

-  Gelişmiş filtreleme
-  Kullanıcı arayüzü
-  Detaylı raporlama
-  Akıllı zamanlama

### 8.3 Faz 3 - Optimizasyon

-  Performans iyileştirmeleri
-  Gelişmiş hata yönetimi
-  Ek özellikler
-  Kullanıcı geri bildirimleri

## 9. Yasal Uyarılar ve Sorumluluk Reddi

Bu otomasyon aracı, Tumblr'ın API kullanım koşullarına ve topluluk kurallarına uygun olarak kullanılmalıdır. Kullanıcılar, aracın kullanımından doğabilecek sonuçlardan kendileri sorumludur. Spam veya kötüye kullanım amaçlı kullanımı yasaktır.
