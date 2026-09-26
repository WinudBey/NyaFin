import pysubs2
from deep_translator import GoogleTranslator
import time
import translators as ts
from core.logger import get_logger
from core.config import Config
from core.exceptions import TranslationError

logger = get_logger(__name__)

class Translator:
    """Handles subtitle parsing and translation via Google Translate (fallback to Bing)."""

    def __init__(self):
        try:
            self.translator = GoogleTranslator(source='auto', target='tr')
            logger.debug("Translator initialized with Google Translate.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {e}")
            raise TranslationError(f"Init Error: {e}")

    def translate_subtitle_file(self, input_sub_path: str, output_sub_path: str, progress_callback=None):
        """
        Parses a subtitle file, translates dialog lines in batches, and saves to a new file.
        Preserves all timestamps and styling.
        
        Args:
            input_sub_path: Path to English .ass/.srt file.
            output_sub_path: Path to save Turkish .ass/.srt file.
            progress_callback: Optional callback for progress (percentage, detail).
        """
        logger.debug(f"Parsing subtitle file: {input_sub_path}")
        
        try:
            subs = pysubs2.load(input_sub_path)
            total_lines = len(subs)
            logger.debug(f"Loaded {total_lines} subtitle lines.")
            
            valid_indices = []
            texts_to_translate = []
            
            for i, line in enumerate(subs):
                if line.text.strip():
                    valid_indices.append(i)
                    texts_to_translate.append(line.text)
                    
            logger.info(f"Translating {len(texts_to_translate)} lines in batches...")
            
            chunk_size = 10  # Daha küçük chunk boyutu Bing'in satırları yutma ihtimalini azaltır
            translated_texts = []
            
            for i in range(0, len(texts_to_translate), chunk_size):
                if Config.STOP_EVENT.is_set():
                    logger.warning("Translation cancelled by user.")
                    raise TranslationError("Cancelled by user.")
                    
                chunk = texts_to_translate[i:i+chunk_size]
                current_chunk = (i // chunk_size) + 1
                total_chunks = (len(texts_to_translate) + chunk_size - 1) // chunk_size
                
                if progress_callback:
                    prog_val = int((current_chunk / total_chunks) * 100)
                    progress_callback(prog_val, f"Bölüm {current_chunk}/{total_chunks} çevriliyor...")
                    
                logger.debug(f"Translating chunk {current_chunk}/{total_chunks}...")
                
                clean_chunk = [t.replace("\n", " ").replace(r"\N", " ") for t in chunk]
                text_to_send = "\n\n".join(clean_chunk)  # Paragrafları ayırmak için çift satır atlama kullanıyoruz
                
                primary_service = Config.TRANSLATOR_PRIMARY_SERVICE
                
                # Build engine try list based on primary service
                engines = [primary_service]
                for fallback in ['google', 'bing', 'yandex', 'alibaba']:
                    if fallback not in engines:
                        engines.append(fallback)
                        
                success = False
                
                for engine in engines:
                    if Config.STOP_EVENT.is_set():
                        raise TranslationError("Cancelled by user.")
                    
                    logger.debug(f"Attempting translation with {engine}...")
                    retries = 2
                    
                    for attempt in range(retries):
                        if Config.STOP_EVENT.is_set():
                            raise TranslationError("Cancelled by user.")
                        try:
                            res = ts.translate_text(text_to_send, translator=engine, from_language='en', to_language='tr')
                            res_lines = res.split("\n")
                            
                            # Clean up empty lines from response
                            res_lines = [line.strip() for line in res_lines if line.strip()]
                            
                            if len(res_lines) == len(chunk):
                                translated_texts.extend(res_lines)
                                success = True
                                time.sleep(1.5)  # Pause to respect rate limits globally
                                break
                            else:
                                logger.warning(f"[{engine}] Chunk length mismatch on attempt {attempt+1}! Expected {len(chunk)}, got {len(res_lines)}.")
                                time.sleep(2.0)
                        except Exception as e:
                            logger.warning(f"[{engine}] API failed on attempt {attempt + 1}: {e}")
                            time.sleep(2.0 * (attempt + 1))
                            
                    if success:
                        break
                        
                if not success:
                    logger.warning("All engines failed batch translation or length mismatch. Falling back to line-by-line with Google...")
                    # Fallback to line by line with delay
                    for text in clean_chunk:
                        if Config.STOP_EVENT.is_set():
                            raise TranslationError("Cancelled by user.")
                        try:
                            # 1 req/sec max to avoid Google limits
                            single_res = ts.translate_text(text, translator='google', from_language='en', to_language='tr')
                            translated_texts.append(single_res)
                            time.sleep(1.1)
                        except Exception as e:
                            logger.error(f"Line-by-line translation failed: {e}")
                            translated_texts.append(text) # Keep original if all else fails
                    success = True
            
            # Map translated lines back to the subtitle objects
            for idx, trans in zip(valid_indices, translated_texts):
                if trans:
                    subs[idx].text = trans
                    
            subs.save(output_sub_path)
            logger.debug(f"Translated subtitle saved to: {output_sub_path}")
            
        except Exception as e:
            logger.error(f"Error processing subtitle file: {e}")
            raise TranslationError(f"Failed to process subtitle file: {e}")

