import codecs
with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

import re
# Fix changeService
content = re.sub(
    r'showToast\(Çeviri servisi \'\' olarak ayarlandı\., "success"\);',
    r'showToast(`Çeviri servisi \'${service}\' olarak ayarlandı.`, "success");',
    content
)
content = re.sub(
    r'appendLog\(>>> \[SİSTEM\] Çeviri servisi \'\' olarak değiştirildi\.\);',
    r'appendLog(`>>> [SİSTEM] Çeviri servisi \'${service}\' olarak değiştirildi.`);',
    content
)

# Wait, previously I fixed changeQuality with Hedef kalite. Let's make sure it's perfect.
content = re.sub(
    r'showToast\(Hedef kalite \'\' olarak ayarlandı\., "success"\);',
    r'showToast(`Hedef kalite \'${qualName}\' olarak ayarlandı.`, "success");',
    content
)
content = re.sub(
    r'appendLog\(>>> \[SİSTEM\] Hedef kalite \'\' olarak değiştirildi\.\);',
    r'appendLog(`>>> [SİSTEM] Hedef kalite \'${qualName}\' olarak değiştirildi.`);',
    content
)

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
