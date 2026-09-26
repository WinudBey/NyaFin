# Görev Adı: Nyaa.si Otomatik İndirme ve Türkçe Altyazı Gömme İş Akışı (Pipeline)

## Bağlam ve Hedef
Nyaa.si üzerinden manuel olarak girilen veya RSS/takip listesi aracılığıyla otomatik olarak tespit edilen anime bölümlerini indiren, içindeki İngilizce altyazıyı çıkartan, Türkçe'ye çeviren ve yeni altyazıyı video dosyasına entegre eden (muxing) uçtan uca bir otomasyon betiği/sistemi geliştirilecek.

## İş Akışı Adımları (Workflow Steps)

### 1. Kaynak Taraması ve Filtreleme (Nyaa.si Scraper/RSS)
*   **Girdi:** Manuel Nyaa URL'si/Magnet linki VEYA takip edilen serilerin RSS beslemesi.
*   **Koşul (Zorunlu):** İndirilecek torrent dosyasının/magnetin metadata'sında veya başlığında İngilizce altyazı (English softsub) bulunduğundan emin ol (örneğin; `[SubsPlease]`, `[Erai-raws]` gibi grupların sürümleri filtrelenebilir).
*   **Çıktı:** İndirilmek üzere sıraya alınmış torrent/magnet bağlantısı.

### 2. İndirme İşlemi (Downloader)
*   **Görev:** Belirlenen torrent dosyasını bir torrent istemcisi (ör. qBittorrent API, Transmission veya aria2) aracılığıyla yerel dizine indir.
*   **Durum Kontrolü:** İndirme işlemi %100 tamamlanana kadar bekle ve indirilen `.mkv` veya `.mp4` dosyasının yolunu (path) bir sonraki adıma ilet.

### 3. Altyazı Çıkartma (Extraction via FFmpeg/MKVToolNix)
*   **Görev:** İndirilen video dosyasını analiz et (ör. `ffprobe` kullanarak) ve içindeki İngilizce altyazı izini (track) bul.
*   **İşlem:** `ffmpeg` veya `mkvextract` kullanarak bu altyazı izini dışa aktar (`.ass` veya `.srt` formatında).

### 4. Çeviri İşlemi (Translation Engine)
*   **Görev:** Dışa aktarılan altyazı dosyasını ayrıştır (parse). Zaman damgalarını (timestamps) ve stil etiketlerini (ör. `.ass` tag'leri) kesinlikle koru.
*   **İşlem:** Sadece metin (dialog) kısımlarını İngilizce'den Türkçe'ye çevir (Kullanılacak API veya yerel LLM modeline metinleri batch halinde gönder).
*   **Çıktı:** Çevirisi tamamlanmış, senkronizasyonu bozulmamış yeni bir Türkçe altyazı dosyası (`TR.ass` veya `TR.srt`).

### 5. Video Birleştirme (Muxing)
*   **Görev:** Orijinal video dosyasını, orijinal ses izini ve yeni oluşturulan Türkçe altyazı dosyasını tek bir `.mkv` dosyası içinde birleştir.
*   **Koşul:** Video ve ses izlerini yeniden kodlamadan (stream copy - `ffmpeg -c copy`) işlemi gerçekleştir. Türkçe altyazıyı "Default" (Varsayılan) iz olarak işaretle.
*   **Çıktı:** İzlenmeye hazır, Türkçe altyazılı son video dosyası.

## Hata Yönetimi (Error Handling)
*   İndirilen videoda "Softsub" (çıkarılabilir altyazı) yoksa işlemi durdur ve loga "Hardsub veya altyazısız sürüm tespit edildi" hatasını yaz.
*   Çeviri sırasında zaman damgalarında kayma veya API hatası oluşursa, işlemi duraklat ve manuel onay bekle.
*   Tamamlanan eski kalıntı dosyaları (geçici altyazılar, ham video) başarı onayından sonra temizle.

## Kullanılacak Araçlar / Kütüphaneler (Öneri)
*   **İndirme:** `aria2c` veya `qbittorrent-api` (Python)
*   **Video/Altyazı İşleme:** `ffmpeg-python`, `ffprobe`, `mkvmerge`
*   **Altyazı Ayrıştırma:** `ass` (Python kütüphanesi) veya `pysrt`
*   **Çeviri:** Local LLM (Ollama API vb.) veya tercih edilen bir çeviri API'si.