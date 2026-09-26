import codecs
with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

# Replace the stray lucide.createIcons();
content = content.replace('// İkonları yükle\n        lucide.createIcons();', '// İkonları yükle')

# Add it to DOMContentLoaded
content = content.replace('loadGroups();', 'loadGroups();\n            lucide.createIcons();')

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
