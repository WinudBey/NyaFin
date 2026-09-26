import os
import ffmpeg
from typing import Optional, Dict
from core.logger import get_logger
from core.config import Config
from core.exceptions import SubtitleExtractError, MuxingError

logger = get_logger(__name__)

class MediaProcessor:
    """Handles all FFmpeg/FFprobe operations for video and subtitles."""

    @staticmethod
    def find_english_subtitle_track(video_path: str) -> Optional[int]:
        """
        Probes the video to find the English subtitle track.
        
        Args:
            video_path: Path to the .mkv/.mp4 file.
            
        Returns:
            Stream index of the English subtitle track, or None.
        """
        logger.debug(f"Probing video: {video_path}")
        try:
            probe = ffmpeg.probe(video_path)
            streams = probe.get('streams', [])
            
            for stream in streams:
                if stream.get('codec_type') == 'subtitle':
                    tags = stream.get('tags', {})
                    # Look for language 'eng' or English title
                    lang = tags.get('language', '').lower()
                    title = tags.get('title', '').lower()
                    
                    if 'eng' in lang or 'eng' in title:
                        logger.debug(f"Found English softsub at stream index {stream['index']}")
                        return stream['index']
                        
            logger.warning("No English softsub track found.")
            return None
        except ffmpeg.Error as e:
            logger.error(f"FFprobe error: {e.stderr.decode() if e.stderr else str(e)}")
            raise SubtitleExtractError(f"Failed to probe video: {e}")

    @staticmethod
    def extract_subtitle(video_path: str, stream_index: int, output_format: str = "ass") -> str:
        """
        Extracts the specified subtitle stream to a file.
        
        Args:
            video_path: Path to the video file.
            stream_index: The index of the subtitle stream to extract.
            output_format: Target format, typically 'ass' or 'srt'.
            
        Returns:
            Path to the extracted subtitle file.
        """
        base_name = os.path.basename(video_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(Config.TEMP_DIR, f"{name_without_ext}_en.{output_format}")
        
        logger.debug(f"Extracting subtitle to: {output_file}")
        
        try:
            # ffmpeg -i input.mkv -map 0:s:0 output.ass
            # We map specific stream, '0:{stream_index}'
            (
                ffmpeg
                .input(video_path)
                .output(output_file, map=f"0:{stream_index}")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.debug("Extraction successful.")
            return output_file
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            logger.error(f"FFmpeg extraction error: {err_msg}")
            raise SubtitleExtractError(f"Extraction failed: {err_msg}")

    @staticmethod
    def mux_video(original_video: str, new_subtitle: str, output_path: Optional[str] = None) -> str:
        """
        Muxes the original video with the new Turkish subtitle.
        Sets the new subtitle as the default track.
        
        Args:
            original_video: Path to original .mkv.
            new_subtitle: Path to the translated .ass/.srt.
            output_path: Path for the final video.
            
        Returns:
            Path to the final muxed video.
        """
        if not output_path:
            base_name = os.path.basename(original_video)
            name_without_ext = os.path.splitext(base_name)[0]
            output_path = os.path.join(Config.OUTPUT_DIR, f"{name_without_ext}_TR.mkv")
            
        logger.debug(f"Muxing new video to: {output_path}")
        
        try:
            # We want to copy all video and audio streams from original, 
            # and add the new subtitle stream as default.
            
            input_vid = ffmpeg.input(original_video)
            input_sub = ffmpeg.input(new_subtitle)
            
            # Map 0:v (all video), 0:a (all audio), 1:s (new sub)
            # -c copy (copy codecs)
            # -c:s ass (since we use ass subtitles)
            # -disposition:s:0 default (make the new sub default)
            
            (
                ffmpeg
                .output(
                    input_vid['v'], 
                    input_vid['a'], 
                    input_sub['s'], 
                    output_path, 
                    vcodec='copy', 
                    acodec='copy', 
                    scodec='ass' if new_subtitle.endswith('.ass') else 'srt',
                    **{'disposition:s:0': 'default'}
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.debug("Muxing successful.")
            return output_path
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            logger.error(f"FFmpeg muxing error: {err_msg}")
            raise MuxingError(f"Muxing failed: {err_msg}")
