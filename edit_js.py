import codecs
with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

new_block = '''function changeService() {
            const service = document.getElementById('serviceSelect').value;
            fetch('/service', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({service: service})
            }).then(r => {
                if(r.ok) {
                    showToast(Çeviri servisi '' olarak ayarlandı., "success");
                    appendLog(>>> [SİSTEM] Çeviri servisi '' olarak değiştirildi.);
                }
            });
        }
        
        function changeQuality() {
            const quality = document.getElementById('qualitySelect').value;
            fetch('/quality', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({quality: quality})
            }).then(r => {
                if(r.ok) {
                    const qualName = quality ? quality : "Tüm Kaliteler";
                    showToast(Hedef kalite '' olarak ayarlandı., "success");
                    appendLog(>>> [SİSTEM] Hedef kalite '' olarak değiştirildi.);
                }
            });
        }'''

# Using substring replacement. The existing changeService function ends just before copyLogs.
# To be safe, we replace unction changeService() { ... } entirely.
old_block = content[content.find('function changeService()'):content.find('function copyLogs()')]
content = content.replace(old_block, new_block + '\n        \n        ')

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
