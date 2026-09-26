
        // İkonları yükle

        // Bildirim fonksiyonu
        function showToast(msg, type = 'success') {
            const colors = {
                'success': 'linear-gradient(to right, #10b981, #059669)',
                'error': 'linear-gradient(to right, #ef4444, #dc2626)',
                'info': 'linear-gradient(to right, #3b82f6, #2563eb)'
            };
            Toastify({
                text: msg,
                duration: 3000,
                gravity: "bottom",
                position: "right",
                stopOnFocus: true,
                style: {
                    background: colors[type] || colors['info'],
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px'
                }
            }).showToast();
        }

        function runAuto() {
            fetch('/run_auto', { method: 'POST' })
                .then(r => {
                    if(r.ok) {
                        showToast("Otomatik çalıştırma başlatıldı.", "success");
                        appendLog(">>> [SİSTEM] Otomatik çalıştırma komutu gönderildi.");
                    } else {
                        showToast("Başlatılamadı!", "error");
                    }
                })
                .catch(() => showToast("Bağlantı hatası", "error"));
        }
        
        function runManual() {
            const url = document.getElementById('manualUrl').value.trim();
            if(!url) {
                showToast("Lütfen bir link girin.", "error");
                return;
            }
            fetch('/run_manual', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            }).then(r => {
                if(r.ok) {
                    showToast("Manuel indirme başlatıldı.", "success");
                    appendLog(">>> [SİSTEM] Manuel indirme komutu gönderildi.");
                    document.getElementById('manualUrl').value = '';
                }
            });
        }
        
        function stopProcess() {
            fetch('/stop', { method: 'POST' })
                .then(r => {
                    if(r.ok) {
                        showToast("Durdurma sinyali gönderildi.", "info");
                        appendLog(">>> [SİSTEM] Durdurma komutu gönderildi.");
                    }
                });
        }
        
        function changeService() {
            const service = document.getElementById('serviceSelect').value;
            fetch('/service', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({service: service})
            }).then(r => {
                if(r.ok) {
                    showToast(`Çeviri servisi \'${service}\' olarak ayarlandı.`, "success");
                    appendLog(`>>> [SİSTEM] Çeviri servisi \'${service}\' olarak değiştirildi.`);
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
                    showToast(`Hedef kalite '${qualName}' olarak ayarlandı.`, "success");
                    appendLog(`>>> [SİSTEM] Hedef kalite '${qualName}' olarak değiştirildi.`);
                }
            });
        }
        
        function copyLogs() {
            const text = document.getElementById('logBox').innerText;
            navigator.clipboard.writeText(text).then(() => {
                showToast("Loglar panoya kopyalandı.", "info");
            });
        }

        function clearLogs() {
            document.getElementById('logBox').innerHTML = '';
            showToast("Loglar temizlendi.", "info");
        }
        
        function loadSeries() {
            fetch('/series')
                .then(r => r.json())
                .then(data => {
                    const list = document.getElementById('seriesList');
                    list.innerHTML = '';
                    if (!data.series || data.series.length === 0) {
                        list.innerHTML = '<li class="text-center text-gray-500 text-sm py-4 border border-dashed border-gray-700 rounded-xl">Takip edilen seri yok.</li>';
                        return;
                    }
                    data.series.forEach(s => {
                        const li = document.createElement('li');
                        li.className = 'flex justify-between items-center p-3 bg-gray-900/50 border border-gray-800 rounded-xl hover:bg-gray-800/50 transition-colors group';
                        
                        const nameSpan = document.createElement('span');
                        nameSpan.className = 'text-sm font-medium text-gray-200 truncate pr-4';
                        nameSpan.textContent = s;
                        
                        const btn = document.createElement('button');
                        btn.className = 'text-gray-500 hover:text-red-400 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all focus:opacity-100 bg-gray-800 hover:bg-red-500/10';
                        btn.title = 'Seriyi Sil';
                        btn.innerHTML = '<i data-lucide="trash-2" class="w-4 h-4"></i>';
                        btn.onclick = () => removeSeries(s);
                        
                        li.appendChild(nameSpan);
                        li.appendChild(btn);
                        list.appendChild(li);
                    });
                    lucide.createIcons();
                });
        }
        
        function addSeries() {
            const name = document.getElementById('seriesName').value.trim();
            if(name) {
                fetch('/series', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name})
                }).then(r => {
                    if(r.ok) {
                        showToast(`'${name}' eklendi.`, "success");
                        document.getElementById('seriesName').value = '';
                        loadSeries();
                    }
                });
            }
        }
        
        function removeSeries(name) {
            fetch('/series', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            }).then(r => {
                if(r.ok) {
                    showToast(`'${name}' silindi.`, "info");
                    loadSeries();
                }
            });
        }

        function loadGroups() {
            fetch('/groups')
                .then(r => r.json())
                .then(data => {
                    if (data.groups) {
                        document.getElementById('targetGroups').value = data.groups.join(', ');
                    }
                })
                .catch(e => console.error("Groups fetch error:", e));
        }

        function saveGroups() {
            const groupsStr = document.getElementById('targetGroups').value;
            fetch('/groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ groups: groupsStr })
            })
            .then(r => r.json())
            .then(data => {
                if(data.status === 'ok') {
                    showToast("Gruplar kaydedildi.", "success");
                    document.getElementById('targetGroups').value = data.groups.join(', ');
                } else {
                    showToast("Gruplar kaydedilemedi!", "error");
                }
            })
            .catch(e => {
                console.error("Groups save error:", e);
                showToast("Bağlantı hatası!", "error");
            });
        }


        function formatLogText(text) {
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
            }

            const regex = /^(\d{2}:\d{2}:\d{2})\s-\s(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s-\s(.*)$/s;
            const match = text.match(regex);
            
            if (match) {
                const [, time, level, msg] = match;
                let levelBadge = "";
                
                switch(level) {
                    case "ERROR":
                    case "CRITICAL":
                        levelBadge = `<span class="bg-red-500/20 text-red-400 border border-red-500/30 px-1.5 rounded text-[11px] font-bold mx-1">ERROR</span>`;
                        break;
                    case "WARNING":
                        levelBadge = `<span class="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-1.5 rounded text-[11px] font-bold mx-1">WARN</span>`;
                        break;
                    case "INFO":
                        levelBadge = `<span class="bg-green-500/20 text-green-400 border border-green-500/30 px-1.5 rounded text-[11px] font-bold mx-1">INFO</span>`;
                        break;
                    case "DEBUG":
                        levelBadge = `<span class="bg-gray-500/20 text-gray-400 border border-gray-500/30 px-1.5 rounded text-[11px] font-bold mx-1">DEBUG</span>`;
                        break;
                }
                
                return `<div class="mb-1 border-b border-gray-800/30 pb-1 last:border-0 hover:bg-gray-800/30 px-1 rounded transition-colors break-words text-gray-300">
                    <span class="text-gray-500">[${time}]</span>${levelBadge}<span class="ml-1">${msg}</span>
                </div>`;
            }

            // Fallback
            let className = "text-gray-300";
            if (text.includes("ERROR") || text.includes("CRITICAL")) className = "text-red-400 font-medium";
            else if (text.includes("WARNING")) className = "text-yellow-400 font-medium";
            else if (text.includes("INFO")) className = "text-green-400";
            else if (text.includes("DEBUG")) className = "text-gray-500";
            
            return `<div class="${className} mb-1 border-b border-gray-800/30 pb-1 last:border-0 hover:bg-gray-800/30 px-1 rounded transition-colors break-words">${text}</div>`;
        }

        function appendLog(msg) {
            const box = document.getElementById('logBox');
            // Auto scroll logic (if user is at the bottom, keep them at the bottom)
            const isScrolledToBottom = box.scrollHeight - box.clientHeight <= box.scrollTop + 50;
            
            box.insertAdjacentHTML('beforeend', formatLogText(msg));
            
            if(isScrolledToBottom) {
                box.scrollTop = box.scrollHeight;
            }
        }

        function pollLogs() {
            fetch('/logs')
                .then(r => r.json())
                .then(data => {
                    if (data.logs && data.logs.length > 0) {
                        data.logs.forEach(log => appendLog(log));
                    }
                }).catch(e => console.error("Log fetch error:", e));
        }

        // Event listener for enter key on input fields
        document.getElementById('seriesName').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') addSeries();
        });
        document.getElementById('manualUrl').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') runManual();
        });

        // Logları saniyede bir çek
        setInterval(pollLogs, 1000);
        
        // Başlangıçta yüklemeler
        document.addEventListener('DOMContentLoaded', () => {
            loadSeries();
            loadGroups();
            lucide.createIcons();
            appendLog(">>> [SİSTEM] NyaFin Web Dashboard başlatıldı. Bağlantı bekleniyor...");
        });
    