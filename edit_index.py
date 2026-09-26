import codecs
with codecs.open('templates/index.html', 'r', 'utf-8') as f:
    content = f.read()

new_block = '''<!-- Kalite Ayarları -->
            <div class="glass-panel rounded-2xl p-5">
                <h3 class="text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                    <i data-lucide="monitor" class="w-4 h-4 text-gray-400"></i>
                    Kalite Seçimi
                </h3>
                <div class="relative">
                    <select id="qualitySelect" onchange="changeQuality()" class="w-full bg-gray-900/80 border border-gray-700 text-gray-200 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 appearance-none">
                        <option value="1080p" {% if target_quality == '1080p' %}selected{% endif %}>1080p</option>
                        <option value="720p" {% if target_quality == '720p' %}selected{% endif %}>720p</option>
                        <option value="480p" {% if target_quality == '480p' %}selected{% endif %}>480p</option>
                        <option value="" {% if target_quality == '' %}selected{% endif %}>Tüm Kaliteler</option>
                    </select>
                    <div class="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
                        <i data-lucide="chevron-down" class="w-4 h-4 text-gray-400"></i>
                    </div>
                </div>
            </div>

            <!-- Grup Ayarları'''

content = content.replace('<!-- Grup Ayarları', new_block)

with codecs.open('templates/index.html', 'w', 'utf-8') as f:
    f.write(content)
