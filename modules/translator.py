import pysubs2
from deep_translator import GoogleTranslator
import time
import translators as ts
from core.logger import get_logger
from core.config import Config
from core.exceptions import TranslationError
import concurrent.futures

logger = get_logger(__name__)

class Translator:
    """Handles subtitle parsing and translation via multiple engines with concurrency."""

    def __init__(self):
        try:
            self.translator = GoogleTranslator(source='auto', target='tr')
            logger.debug("Translator initialized with Google Translate.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {e}")
            raise TranslationError(f"Init Error: {e}")

    def translate_subtitle_file(self, input_sub_path: str, output_sub_path: str, progress_callback=None):
        """
        Parses a subtitle file, translates dialog lines concurrently in batches using multiple engines.
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
                    
            logger.info(f"Translating {len(texts_to_translate)} lines concurrently in batches...")
            
            chunk_size = 10
            chunks = [texts_to_translate[i:i+chunk_size] for i in range(0, len(texts_to_translate), chunk_size)]
            translated_results = [None] * len(chunks)
            
            primary_service = Config.TRANSLATOR_PRIMARY_SERVICE
            engines = [primary_service]
            for fallback in ['google', 'bing', 'yandex', 'alibaba']:
                if fallback not in engines:
                    engines.append(fallback)
                    
            def translate_chunk(chunk_idx, chunk_text_list):
                if Config.STOP_EVENT.is_set():
                    return None
                    
                clean_chunk = [t.replace("\n", " ").replace(r"\N", " ") for t in chunk_text_list]
                text_to_send = "\n\n".join(clean_chunk)
                
                # Start with a different engine based on chunk_idx to distribute load across threads
                start_idx = chunk_idx % len(engines)
                
                for attempt in range(len(engines)):
                    if Config.STOP_EVENT.is_set():
                        return None
                        
                    engine = engines[(start_idx + attempt) % len(engines)]
                    
                    try:
                        res = ts.translate_text(text_to_send, translator=engine, from_language='en', to_language='tr')
                        res_lines = [line.strip() for line in res.split("\n") if line.strip()]
                        
                        if len(res_lines) == len(chunk_text_list):
                            # Detect if API silently failed and echoed English back (common with ASS tags)
                            is_echo = True
                            for orig, translated in zip(clean_chunk, res_lines):
                                if orig.strip() != translated.strip():
                                    is_echo = False
                                    break
                                    
                            if is_echo:
                                logger.debug(f"[{engine}] Echoed original text in chunk {chunk_idx}. Treating as failure.")
                                continue
                                
                            time.sleep(0.3) # Tiny delay to prevent spamming
                            return res_lines
                        else:
                            logger.debug(f"[{engine}] Mismatch in chunk {chunk_idx}. Expected {len(chunk_text_list)}, got {len(res_lines)}.")
                    except Exception as e:
                        logger.debug(f"[{engine}] API error in chunk {chunk_idx}: {e}")
                
                # If all batch engines fail, fallback to single line translation
                logger.warning(f"Chunk {chunk_idx} batch failed entirely. Using line-by-line fallback.")
                fallback_lines = []
                for text in clean_chunk:
                    if Config.STOP_EVENT.is_set():
                        return None
                    try:
                        single_res = ts.translate_text(text, translator='google', from_language='en', to_language='tr')
                        fallback_lines.append(single_res)
                        time.sleep(0.5)
                    except Exception:
                        try:
                            single_res = ts.translate_text(text, translator='bing', from_language='en', to_language='tr')
                            fallback_lines.append(single_res)
                            time.sleep(0.5)
                        except Exception:
                            fallback_lines.append(text)
                return fallback_lines

            completed = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(translate_chunk, i, chunk): i for i, chunk in enumerate(chunks)}
                
                for future in concurrent.futures.as_completed(futures):
                    if Config.STOP_EVENT.is_set():
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise TranslationError("Cancelled by user.")
                        
                    idx = futures[future]
                    res = future.result()
                    
                    if res is None and Config.STOP_EVENT.is_set():
                        raise TranslationError("Cancelled by user.")
                        
                    translated_results[idx] = res
                    completed += 1
                    
                    if progress_callback:
                        prog_val = int((completed / len(chunks)) * 100)
                        progress_callback(prog_val, f"Cevriliyor... ({completed}/{len(chunks)} paket)")

            # Flatten results
            translated_texts = []
            for res_list in translated_results:
                if res_list:
                    translated_texts.extend(res_list)
            
            # Map translated lines back
            for idx, trans in zip(valid_indices, translated_texts):
                if trans:
                    subs[idx].text = trans
                    
            subs.save(output_sub_path)
            logger.debug(f"Translated subtitle saved to: {output_sub_path}")
            
        except Exception as e:
            logger.error(f"Error processing subtitle file: {e}")
            raise TranslationError(f"Failed to process subtitle file: {e}")
