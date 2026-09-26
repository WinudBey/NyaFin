import os
import threading
import queue
import logging
from flask import Flask, render_template, request, jsonify
from pipeline import Pipeline
from core.logger import get_logger
from core.config import Config

app = Flask(__name__)
logger = get_logger(__name__)

# Canlı logları web arayüzüne aktarmak için kuyruk yapısı
log_queue = queue.Queue()
class QueueLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        log_queue.put(msg)

gui_handler = QueueLogHandler()
gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
for name in ['core.logger', 'pipeline', 'modules.scraper', 'modules.downloader', 'modules.media', 'modules.translator', '__main__']:
    logging.getLogger(name).addHandler(gui_handler)

try:
    pipeline = Pipeline()
except Exception as e:
    logger.error(f"Failed to init pipeline: {e}")
    pipeline = None

@app.route('/')
def index():
    return render_template('index.html', qb_host=Config.QB_HOST, qb_user=Config.QB_USER, primary_service=Config.TRANSLATOR_PRIMARY_SERVICE, target_quality=Config.TARGET_QUALITY)

@app.route('/logs')
def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())
    return jsonify({"logs": logs})

@app.route('/run_auto', methods=['POST'])
def run_auto():
    if not pipeline:
        return jsonify({"error": "Pipeline başlatılamadı."}), 500
    threading.Thread(target=pipeline.run_auto, daemon=True).start()
    return jsonify({"status": "Auto run started"})

@app.route('/run_manual', methods=['POST'])
def run_manual():
    if not pipeline:
        return jsonify({"error": "Pipeline başlatılamadı."}), 500
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "URL gerekli."}), 400
    threading.Thread(target=pipeline.run_manual, args=(url,), daemon=True).start()
    return jsonify({"status": "Manual run started"})
    
@app.route('/stop', methods=['POST'])
def stop_process():
    Config.STOP_EVENT.set()
    logger.warning("İşlem durdurma sinyali (Web üzerinden) gönderildi.")
    return jsonify({"status": "Stop signal sent"})

@app.route('/service', methods=['GET', 'POST'])
def manage_service():
    if request.method == 'POST':
        service = request.json.get("service")
        if service in ["bing", "google"]:
            Config.TRANSLATOR_PRIMARY_SERVICE = service
            logger.info(f"Çeviri servisi (Web üzerinden) '{service}' olarak değiştirildi.")
            return jsonify({"status": "ok", "service": service})
        return jsonify({"error": "Geçersiz servis"}), 400
    return jsonify({"service": Config.TRANSLATOR_PRIMARY_SERVICE})

@app.route('/quality', methods=['GET', 'POST'])
def manage_quality():
    if request.method == 'POST':
        quality = request.json.get("quality")
        if quality in ["1080p", "720p", "480p", ""]:
            Config.TARGET_QUALITY = quality
            logger.info(f"Hedef kalite (Web üzerinden) '{quality}' olarak değiştirildi.")
            return jsonify({"status": "ok", "quality": quality})
        return jsonify({"error": "Geçersiz kalite"}), 400
    return jsonify({"quality": Config.TARGET_QUALITY})

@app.route('/groups', methods=['GET', 'POST'])
def manage_groups():
    if request.method == 'POST':
        groups_str = request.json.get("groups")
        if groups_str is not None:
            Config.TARGET_GROUPS = [g.strip() for g in groups_str.split(",") if g.strip()]
            logger.info(f"Hedef gruplar (Web üzerinden) güncellendi: {Config.TARGET_GROUPS}")
            return jsonify({"status": "ok", "groups": Config.TARGET_GROUPS})
        return jsonify({"error": "Geçersiz veriler"}), 400
    return jsonify({"groups": Config.TARGET_GROUPS})


@app.route('/series', methods=['GET', 'POST', 'DELETE'])
def manage_series():
    if not pipeline:
        return jsonify({"error": "Pipeline başlatılamadı."}), 500
    
    if request.method == 'GET':
        return jsonify({"series": pipeline.tracker.get_tracked_series()})
    
    if request.method == 'POST':
        name = request.json.get("name")
        if name:
            pipeline.tracker.add_series(name)
        return jsonify({"status": "ok"})
        
    if request.method == 'DELETE':
        name = request.json.get("name")
        if name:
            pipeline.tracker.remove_series(name)
        return jsonify({"status": "ok"})

@app.route('/reset_db', methods=['POST'])
def reset_db():
    if not pipeline:
        return jsonify({"error": "Pipeline başlatılamadı."}), 500
    pipeline.tracker.reset_db()
    logger.warning("Veritabanı (series_db.json) sıfırlandı.")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # 0.0.0.0 ile homelab ağındaki tüm cihazlardan erişilebilir
    app.run(host='0.0.0.0', port=5000)
