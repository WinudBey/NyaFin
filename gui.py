import customtkinter as ctk
import threading
import queue
import logging
from pipeline import Pipeline
from core.logger import get_logger

logger = get_logger(__name__)

class TextboxLogHandler(logging.Handler):
    """A logging handler that puts logs into a thread-safe queue for the GUI."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)


class NyaFinApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NyaFin - Anime Otomasyonu")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.log_queue = queue.Queue()
        
        try:
            self.pipeline = Pipeline()
        except Exception as e:
            logger.error(f"Başlangıç hatası: {e}")
            logger.error("Lütfen 'Ayarlar' sekmesinden bağlantı bilgilerinizi güncelleyin.")
            # pipeline might be partially initialized, but we can recreate it after settings are saved.
            self.pipeline = None
        
        self.setup_ui()
        self.setup_logging()
        
        # Start periodic log checking
        self.check_log_queue()

    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        self.label_title = ctk.CTkLabel(self, text="NyaFin İş Akışı Yönetimi", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Controls Frame
        self.frame_controls = ctk.CTkFrame(self)
        self.frame_controls.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_controls.grid_columnconfigure(1, weight=1)

        # Auto RSS Button
        self.btn_auto = ctk.CTkButton(self.frame_controls, text="Otomatik Çalıştır (RSS)", command=self.run_auto_thread)
        self.btn_auto.grid(row=0, column=0, padx=10, pady=10)

        # Manual URL Input
        self.entry_url = ctk.CTkEntry(self.frame_controls, placeholder_text="Manuel Torrent / Magnet URL'si girin...")
        self.entry_url.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Manual Run Button
        self.btn_manual = ctk.CTkButton(self.frame_controls, text="İndir ve Çevir", command=self.run_manual_thread)
        self.btn_manual.grid(row=0, column=2, padx=10, pady=10)
        
        # Stop Button
        self.btn_stop = ctk.CTkButton(self.frame_controls, text="Durdur ⏹", fg_color="red", hover_color="darkred", command=self.stop_process)
        self.btn_stop.grid(row=0, column=3, padx=10, pady=10)
        
        # Settings Button
        self.btn_settings = ctk.CTkButton(self.frame_controls, text="Ayarlar ⚙️", fg_color="gray", command=self.open_settings)
        self.btn_settings.grid(row=0, column=4, padx=10, pady=10)
        
        # Tracker Button
        self.btn_tracker = ctk.CTkButton(self.frame_controls, text="Seri Takip 📋", fg_color="purple", command=self.open_tracker)
        self.btn_tracker.grid(row=0, column=5, padx=10, pady=10)

        # Secondary Controls Frame
        self.frame_secondary = ctk.CTkFrame(self)
        self.frame_secondary.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.label_service = ctk.CTkLabel(self.frame_secondary, text="Birincil Çeviri Servisi:")
        self.label_service.pack(side="left", padx=10, pady=5)
        
        from core.config import Config
        self.var_service = ctk.StringVar(value=Config.TRANSLATOR_PRIMARY_SERVICE)
        self.opt_service = ctk.CTkOptionMenu(self.frame_secondary, values=["bing", "google"], variable=self.var_service, command=self.change_service)
        self.opt_service.pack(side="left", padx=10, pady=5)

        self.btn_copy_logs = ctk.CTkButton(self.frame_secondary, text="Logları Kopyala 📋", fg_color="#444", command=self.copy_logs)
        self.btn_copy_logs.pack(side="right", padx=10, pady=5)

        # Log Textbox
        self.textbox_logs = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 12))
        self.textbox_logs.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")

    def change_service(self, choice):
        from core.config import Config
        Config.TRANSLATOR_PRIMARY_SERVICE = choice
        logger.info(f"Çeviri servisi '{choice}' olarak değiştirildi.")

    def stop_process(self):
        from core.config import Config
        Config.STOP_EVENT.set()
        logger.warning("İşlem durdurma sinyali gönderildi. Mevcut işlem bitince duracak.")
        
    def copy_logs(self):
        self.clipboard_clear()
        logs = self.textbox_logs.get("1.0", ctk.END)
        self.clipboard_append(logs)
        logger.info("Loglar panoya kopyalandı.")

    def open_tracker(self):
        """Açılır pencere (Modal) ile takip edilen serileri yönetir."""
        if not self.pipeline:
            logger.error("Sistem başlatılamadı. Lütfen Ayarlar'dan qBittorrent bağlantısını düzeltin.")
            return
            
        tracker_window = ctk.CTkToplevel(self)
        tracker_window.title("Seri Takip Yönetimi")
        tracker_window.geometry("500x400")
        tracker_window.grab_set() # Focus on this window
        
        ctk.CTkLabel(tracker_window, text="Takip Edilen Seriler", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Listbox for series
        # CustomTkinter doesn't have a native Listbox, we can use a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tracker_window, width=400, height=200)
        scroll_frame.pack(pady=10)
        
        def refresh_list():
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            tracked = self.pipeline.tracker.get_tracked_series()
            for series in tracked:
                row = ctk.CTkFrame(scroll_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=series).pack(side="left", padx=10)
                btn_del = ctk.CTkButton(row, text="Sil", width=50, fg_color="red", command=lambda s=series: remove_series(s))
                btn_del.pack(side="right", padx=10)
                
        def remove_series(series_name):
            self.pipeline.tracker.remove_series(series_name)
            refresh_list()
            
        def add_series():
            new_series = entry_add.get().strip()
            if new_series:
                self.pipeline.tracker.add_series(new_series)
                entry_add.delete(0, ctk.END)
                refresh_list()
                
        refresh_list()
        
        frame_add = ctk.CTkFrame(tracker_window)
        frame_add.pack(pady=10, fill="x", padx=40)
        
        entry_add = ctk.CTkEntry(frame_add, placeholder_text="Örn: Mushoku Tensei")
        entry_add.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_add = ctk.CTkButton(frame_add, text="Ekle", width=80, command=add_series)
        btn_add.pack(side="right")

    def open_settings(self):
        """Açılır pencere (Modal) ile kullanıcıdan qBittorrent bilgilerini ister."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Ayarlar")
        settings_window.geometry("400x350")
        settings_window.grab_set() # Focus on this window
        
        # Host
        ctk.CTkLabel(settings_window, text="qBittorrent Host (URL):").pack(pady=(20, 5))
        entry_host = ctk.CTkEntry(settings_window, width=300)
        from core.config import Config
        entry_host.insert(0, Config.QB_HOST)
        entry_host.pack()

        # Username
        ctk.CTkLabel(settings_window, text="Kullanıcı Adı:").pack(pady=(10, 5))
        entry_user = ctk.CTkEntry(settings_window, width=300)
        entry_user.insert(0, Config.QB_USER)
        entry_user.pack()

        # Password
        ctk.CTkLabel(settings_window, text="Şifre (API Key):").pack(pady=(10, 5))
        entry_pass = ctk.CTkEntry(settings_window, width=300, show="*")
        entry_pass.insert(0, Config.QB_PASS)
        entry_pass.pack()

        def save_settings():
            import os
            from dotenv import set_key
            env_file = os.path.join(Config.BASE_DIR, ".env")
            
            # Save to .env
            set_key(env_file, "QB_HOST", entry_host.get())
            set_key(env_file, "QB_USER", entry_user.get())
            set_key(env_file, "QB_PASS", entry_pass.get())
            
            # Update memory
            Config.QB_HOST = entry_host.get()
            Config.QB_USER = entry_user.get()
            Config.QB_PASS = entry_pass.get()
            
            # Recreate pipeline entirely
            try:
                self.pipeline = Pipeline()
                logger.info("Ayarlar başarıyla kaydedildi ve istemci bağlandı.")
                settings_window.destroy()
            except Exception as e:
                logger.error(f"Bağlantı başarısız: {e}")

        ctk.CTkButton(settings_window, text="Kaydet", command=save_settings).pack(pady=20)

    def setup_logging(self):
        # Attach our custom handler to the root logger or the specific ones
        # For simplicity, let's attach to the root logger of the core
        gui_handler = TextboxLogHandler(self.log_queue)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        
        # Attach to the main app loggers
        for name in ['core.logger', 'pipeline', 'modules.scraper', 'modules.downloader', 'modules.media', 'modules.translator', '__main__']:
            log = logging.getLogger(name)
            log.addHandler(gui_handler)

    def check_log_queue(self):
        """Polls the queue and updates the GUI text box."""
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.textbox_logs.configure(state="normal")
            self.textbox_logs.insert(ctk.END, msg + "\n")
            self.textbox_logs.configure(state="disabled")
            self.textbox_logs.see(ctk.END) # Scroll to bottom
            
        self.after(100, self.check_log_queue)

    def set_buttons_state(self, state):
        self.btn_auto.configure(state=state)
        self.btn_manual.configure(state=state)
        # We don't disable btn_stop because we want user to be able to click it anytime

    def run_auto_thread(self):
        if not self.pipeline:
            logger.error("Sistem başlatılamadı. Lütfen Ayarlar'dan qBittorrent bağlantısını düzeltin.")
            return
        self.set_buttons_state("disabled")
        threading.Thread(target=self._auto_task, daemon=True).start()

    def run_manual_thread(self):
        if not self.pipeline:
            logger.error("Sistem başlatılamadı. Lütfen Ayarlar'dan qBittorrent bağlantısını düzeltin.")
            return
        url = self.entry_url.get().strip()
        if not url:
            logger.warning("Lütfen manuel indirme için geçerli bir URL girin.")
            return
            
        self.set_buttons_state("disabled")
        threading.Thread(target=self._manual_task, args=(url,), daemon=True).start()

    def _auto_task(self):
        try:
            self.pipeline.run_auto()
        except Exception as e:
            logger.error(f"Otomatik işlem hatası: {e}")
        finally:
            self.set_buttons_state("normal")

    def _manual_task(self, url):
        try:
            self.pipeline.run_manual(url)
        except Exception as e:
            logger.error(f"Manuel işlem hatası: {e}")
        finally:
            self.set_buttons_state("normal")


if __name__ == "__main__":
    app = NyaFinApp()
    app.mainloop()
