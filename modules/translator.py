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

    def translate_subtitle_file(self, input_sub_path: str, output_sub_path: str):
        """
        Parses a subtitle file, translates dialog lines in batches, and saves to a new file.
        Preserves all timestamps and styling.
        
        Args:
            input_sub_path: Path to English .ass/.srt file.
            output_sub_path: Path to save Turkish .ass/.srt file.
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
            
            chunk_size = 20
            translated_texts = []
            
            for i in range(0, len(texts_to_translate), chunk_size):
                if Config.STOP_EVENT.is_set():
                    logger.warning("Translation cancelled by user.")
                    raise TranslationError("Cancelled by user.")
                    
                chunk = texts_to_translate[i:i+chunk_size]
                logger.debug(f"Translating chunk {i//chunk_size + 1}/{(len(texts_to_translate) + chunk_size - 1)//chunk_size}...")
                
                success = False
                retries = 3
                
                clean_chunk = [t.replace("\n", " ").replace(r"\N", " ") for t in chunk]
                text_to_send = "\n".join(clean_chunk)
                
                primary_service = Config.TRANSLATOR_PRIMARY_SERVICE
                
                def try_bing():
                    nonlocal success
                    for attempt in range(retries):
                        if Config.STOP_EVENT.is_set(): return False
                        try:
                            res = ts.translate_text(text_to_send, translator='bing', from_language='en', to_language='tr')
                            res_lines = res.split("\n")
                            
                            if len(res_lines) == len(chunk):
                                translated_texts.extend(res_lines)
                            else:
                                logger.warning(f"Bing chunk length mismatch! Expected {len(chunk)}, got {len(res_lines)}. Translating line by line...")
                                for text in clean_chunk:
                                    if Config.STOP_EVENT.is_set(): return False
                                    single_res = ts.translate_text(text, translator='bing', from_language='en', to_language='tr')
                                    translated_texts.append(single_res)
                                    time.sleep(0.5)
                            
                            success = True
                            time.sleep(1.0)
                            return True
                        except Exception as e:
                            logger.warning(f"Bing Translate API failed on attempt {attempt + 1}: {e}")
                            time.sleep(2.0 * (attempt + 1))
                    return False
                    
                def try_google():
                    nonlocal success
                    logger.info("Attempting Google Translate...")
                    try:
                        res = self.translator.translate_batch(chunk)
                        translated_texts.extend(res)
                        success = True
                        time.sleep(2.0)
                        return True
                    except Exception as e:
                        logger.error(f"Google Translate API failed: {e}")
                        return False
                
                if primary_service == "bing":
                    if not try_bing():
                        logger.warning("Primary (Bing) failed. Falling back to Google...")
                        if not try_google():
                            raise TranslationError("API Error on batch: Both engines failed.")
                else:
                    if not try_google():
                        logger.warning("Primary (Google) failed. Falling back to Bing...")
                        if not try_bing():
                            raise TranslationError("API Error on batch: Both engines failed.")
            
            # Map translated lines back to the subtitle objects
            for idx, trans in zip(valid_indices, translated_texts):
                if trans:
                    subs[idx].text = trans
                    
            subs.save(output_sub_path)
            logger.debug(f"Translated subtitle saved to: {output_sub_path}")
            
        except Exception as e:
            logger.error(f"Error processing subtitle file: {e}")
            raise TranslationError(f"Failed to process subtitle file: {e}")

