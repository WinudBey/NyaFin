import codecs
import re

with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

old_block = """        function formatLogText(text) {
            if (text.startsWith(">>> [SİSTEM]")) {
                return `<div class="text-indigo-400 font-bold mb-1 border-b border-gray-800/30 pb-1 last:border-0 hover:bg-gray-800/30 px-1 rounded transition-colors break-words">${text}</div>`;
            }"""

new_block = """        function formatLogText(text) {
            if (text.startsWith(">>> [SİSTEM]")) {
                const now = new Date();
                const timeStr = [
                    now.getHours().toString().padStart(2, '0'),
                    now.getMinutes().toString().padStart(2, '0'),
                    now.getSeconds().toString().padStart(2, '0')
                ].join(':');
                const msg = text.replace(">>> [SİSTEM] ", "");
                const badge = `<span class="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-1.5 rounded text-[11px] font-bold mx-1">SİSTEM</span>`;
                
                return `<div class="mb-1 border-b border-gray-800/30 pb-1 last:border-0 hover:bg-gray-800/30 px-1 rounded transition-colors break-words text-gray-300">
                    <span class="text-gray-500">[${timeStr}]</span>${badge}<span class="ml-1 text-indigo-300 font-medium">${msg}</span>
                </div>`;
            }"""

content = content.replace(old_block, new_block)

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
