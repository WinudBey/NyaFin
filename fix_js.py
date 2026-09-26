import codecs
with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('showToast(Hedef kalite \'\' olarak ayarlandı., "success");', 'showToast(`Hedef kalite \'${qualName}\' olarak ayarlandı.`, "success");')
content = content.replace('appendLog(>>> [SİSTEM] Hedef kalite \'\' olarak değiştirildi.);', 'appendLog(`>>> [SİSTEM] Hedef kalite \'${qualName}\' olarak değiştirildi.`);')

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
