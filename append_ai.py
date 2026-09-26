from datetime import datetime
import codecs

now = datetime.now().strftime("%Y-%m-%d %H:%M")
entry = f"\n- **[{now}]** - Faz 11 (Kalite Seçimi) tamamlandı. Web arayüzüne \"Kalite Seçimi\" (1080p, 720p, 480p, Tüm Kaliteler) açılır menüsü eklendi. Seçimler dinamik olarak RSS arama URL'sini (NYAA_RSS_URL) güncelleyerek Scraper'ın istenen çözünürlükteki videoları indirmesini sağlıyor.\n"

with codecs.open('ai.md', 'a', 'utf-8') as f:
    f.write(entry)
