# NyaFin - Proje Hafızası (ai.md)

## Proje Hakkında
Nyaa.si üzerinden otomatik anime indirme, altyazı çıkarma (İngilizce), yerel LLM (Ollama) ile çeviri (Türkçe) yapma ve tekrar videoya "softsub" olarak gömme projesi.

## Zaman Çizelgesi ve Yapılanlar

- **[2026-09-26 17:25]** - Proje başlatıldı. "/goal" komutu ile tüm modüllerin ardışık olarak otomatik geliştirilmesi kararı alındı.
- **[2026-09-26 17:25]** - Faz 1 (Altyapı) başladı. `core`, `modules`, `tests`, `data` ve `logs` klasör yapıları ile temel dosyalar oluşturuluyor.
- **[2026-09-26 17:26]** - Faz 1 tamamlandı. Faz 2 (Scraper Modülü) geliştirmesine başlandı.
- **[2026-09-26 17:28]** - Faz 2 ve Faz 3 tamamlandı. Scraper ve Downloader modülleri yazıldı.
- **[2026-09-26 17:29]** - Faz 4 ve Faz 5 tamamlandı. Media (FFmpeg) ve Translator (Ollama + pysubs2) modülleri ve testleri yazıldı. Faz 6 (Pipeline) aşamasına geçiliyor.
- **[2026-09-26 17:30]** - Faz 6 tamamlandı. `pipeline.py` ve `main.py` oluşturuldu. Tüm modüller birbiriyle bağlandı. Temel iş akışı tamamlandı.
- **[2026-09-26 17:32]** - "/goal bide gui ekle" talebi üzerine Faz 7 (Grafik Arayüz - GUI) geliştirmesine başlandı. `customtkinter` eklendi.
- **[2026-09-26 17:33]** - Faz 7 (GUI) tamamlandı. `customtkinter` kullanılarak logları gerçek zamanlı gösteren ve süreci dondurmayan (multi-threading) modern bir arayüz yazıldı (`gui.py`).
- **[2026-09-26 17:36]** - `nyaa.si/view/ID` linklerinin indirmede başarısız olması hatası çözüldü. Video dosyası bulunamadı hatası düzeltildi (video dosya uzantısını hesaba katarak bulması için `torrents_files` kullanıldı).
- **[2026-09-26 17:38]** - FFmpeg'in sistemde kurulu olmadığı tespit edildi (FileNotFoundError [WinError 2]). Winget kullanılarak `Gyan.FFmpeg.Essentials` paketi sisteme yüklendi.
- **[2026-09-26 18:12]** - Ollama yerine çeviri altyapısı `deep-translator` kullanılarak Google Çeviri'ye (Google Translate) yönlendirildi. `modules/translator.py` güncellendi.

- **[2026-09-26 18:15]** - `deep-translator` kütüphanesi sanal ortama (venv) yüklendi ve `requirements.txt` dosyasına eklendi.
- **[2026-09-26 18:20]** - Google Translate API'sindeki limit (5 requests per second) aşıldığı için, `modules/translator.py` dosyasına `translate_batch` metodu ve "chunking" (parçalama) algoritması eklendi. Altyazılar artık 30 satırlık bloklar halinde, aralarında 1.5 saniye bekleyerek çevriliyor.
- **[2026-09-26 18:25]** - Google Translate'in katı IP kısıtlamaları (Rate Limit) aşılamadığı için çeviri altyapısı `translators` kütüphanesi ile **Bing Translate** motoruna taşındı. Çeviriler yine 20 satırlık toplu bloklar (chunking) halinde yapılıyor ve satır kayması olursa otomatik tekil çeviriye düşecek bir hata kontrol (fallback) mekanizması eklendi.
- **[2026-09-26 23:35]** - Faz 8 tamamlandı. Kullanıcıdan alınan onayla "Seri Takip Sistemi" (Tracker) modülü projeye entegre edildi. Arayüze "Seri Takip Yönetimi" butonu eklendi. Sistem artık Nyaa başlıklarını Regex ile parçalayıp, sadece kullanıcının takip ettiği serilerin **daha önce indirilmemiş yeni bölümlerini** otomatik olarak indiriyor.
- **[2026-09-26 23:39]** - Faz 9 tamamlandı. Kullanıcının projesi bir "Homelab" ortamında masaüstü arabirimi olmadan (headless) çalışacağı için, Flask kullanılarak tam fonksiyonel bir **Web Arayüzü (Dashboard)** eklendi (`web.py` ve `templates/index.html`). Tüm log takibi ve seri yönetim işlemleri artık herhangi bir cihazın tarayıcısından 5000 portu üzerinden yapılabiliyor.
- **[2026-09-26 23:45]** - `translator.py` içerisindeki Google ve Bing Translate çakışması (duplicate append) ve hız sınırlaması (rate limit) sorunları düzeltildi. Çeviri sistemi öncelikle Google Translate API'si (batch translate) üzerinden, exponential backoff (artan bekleme süreleri) ve retry mekanizmasıyla çalışacak şekilde yapılandırıldı. Hata durumunda (rate limit) Bing motoruna fallback yapması sağlandı. Çift listeye ekleme hatası giderilerek çevirideki satır kayması (mismatch) kalıcı olarak onarıldı.
- **[2026-09-26 23:50]** - Google Translate API'sinin kullanıcının IP'sini kalıcı olarak (hard) rate-limit ile kısıtladığı ve sürekli 3 denemeyi boşa harcattığı tespit edildi. API bekleme sürelerinin performansı çok düşürmesi (her chunk için gereksiz ~20 saniye gecikme) nedeniyle **Birincil Çeviri Motoru Bing Translate'e geçirildi**. Google Translate sadece acil durum yedeği (fallback) olarak bırakıldı.

- **[2026-09-26 23:55]** - Faz 10 (Kullanıcı Deneyimi İyileştirmeleri) tamamlandı. Kullanıcı isteği üzerine; hem Masaüstü GUI (`gui.py`) hem de Web Arayüzü (`index.html` & `web.py`) içerisine "İşlemi Durdurma", "Çeviri Servisi Seçimi (Bing/Google)", ve "Logları Kopyalama" özellikleri eklendi. `threading.Event` kullanılarak güvenli bir işlem durdurma (cancellation) mekanizması `pipeline.py`, `downloader.py` ve `translator.py` içine entegre edildi. Çeviri motorları arasındaki (Primary/Fallback) hiyerarşi artık arayüz üzerinden dinamik olarak değiştirilebiliyor.

- **[2026-09-26 23:57]** - Kullanıcı geri bildirimi üzerine Web Arayüzünde (`index.html`) tasarım düzenlemesi yapıldı. "Çeviri Ayarları" bölümü sol sütundan ayrılarak sağ sütundaki "Seri Takip Yönetimi" panelinin altına ayrı bir kart olarak taşındı.

- **[2026-09-26 23:59]** - Bing Çeviri servisi kullanırken oluşan `chunk length mismatch (Expected 20, got 1)` hatası düzeltildi. Bing'in satır sonu karakterlerini (`\n`) yutup tek bir paragraf olarak geri döndürmesini engellemek için, metin blokları arasına çift satır sonu (`\n\n`) eklenerek ayrı paragraflar (paragraphs) şeklinde gönderilmesi ve yanıtın boş satırlardan temizlenerek (`strip`) alınması sağlandı. Böylece zorunlu "tek tek çeviri" (fallback) moduna düşülmesinin büyük oranda önüne geçildi.
- **[2026-09-27 00:09]** - Kullanıcının talebi üzerine Web Arayüzü (`templates/index.html`) modernize edilerek baştan yazıldı. Tasarımda Tailwind CSS ve Lucide Icons kullanıldı. "Glassmorphism" ve koyu tema (Dark Mode) birleştirilerek şık bir görünüm elde edildi. İşlem bildirimleri için "Toastify" kütüphanesi eklendi. Canlı log akışı renklendirilerek kod editörü hissiyatı verildi. Backend (`web.py`) aynı kalarak sorunsuz geçiş sağlandı.
- **[2026-09-27 00:20]** - Web arayüzüne "Tercih Edilen Gruplar" (Preferred Groups) yönetim paneli eklendi (`templates/index.html` ve `web.py`). Artık kullanıcılar hedef çeviri gruplarını arayüz üzerinden düzenleyebilecekler.

- **[2026-09-27 00:26]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne "Kalite Seçimi" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.

- **[2026-09-27 00:41]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne "Kalite Seçimi" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.

- **[2026-09-27 00:48]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne "Kalite Seçimi" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.

- **[2026-09-27 00:49]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne "Kalite Seçimi" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.

- **[2026-09-27 00:59]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne "Kalite Seçimi" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.

- **[2026-09-27 01:03]** - Eksikleri arama (Search) isleminde bolumlerin sondan basa (ornegin 1'den degil 12'den baslayarak) indirilmesi sorunu cozuldu. `tracker.py` icerisindeki eksik bolumlerin listelendigi fonksiyona bolum numarasina gore kucukten buyuge (ascending) siralama islemi eklendi.
