class NyaFinException(Exception):
    """Base exception class for all NyaFin custom exceptions."""
    pass

class SubtitleExtractError(NyaFinException):
    """Raised when English softsubs cannot be extracted or found in the video."""
    pass

class TranslationError(NyaFinException):
    """Raised when the translation engine fails or times out."""
    pass

class MuxingError(NyaFinException):
    """Raised when FFmpeg fails to mux the final output video."""
    pass

class DownloadError(NyaFinException):
    """Raised when there is an issue with the download client (e.g., qBittorrent unreachable)."""
    pass

class ScraperError(NyaFinException):
    """Raised when Nyaa.si cannot be reached or parsed correctly."""
    pass
