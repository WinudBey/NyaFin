import pytest
from unittest.mock import patch, MagicMock
from modules.media import MediaProcessor
from core.exceptions import SubtitleExtractError

@patch('modules.media.ffmpeg.probe')
def test_find_english_subtitle_track_success(mock_probe):
    # Mock ffprobe output
    mock_probe.return_value = {
        'streams': [
            {'index': 0, 'codec_type': 'video'},
            {'index': 1, 'codec_type': 'audio'},
            {'index': 2, 'codec_type': 'subtitle', 'tags': {'language': 'eng', 'title': 'English (US)'}},
            {'index': 3, 'codec_type': 'subtitle', 'tags': {'language': 'spa'}}
        ]
    }
    
    index = MediaProcessor.find_english_subtitle_track("dummy.mkv")
    assert index == 2

@patch('modules.media.ffmpeg.probe')
def test_find_english_subtitle_track_not_found(mock_probe):
    mock_probe.return_value = {
        'streams': [
            {'index': 0, 'codec_type': 'video'},
            {'index': 1, 'codec_type': 'subtitle', 'tags': {'language': 'jpn'}}
        ]
    }
    
    index = MediaProcessor.find_english_subtitle_track("dummy.mkv")
    assert index is None
