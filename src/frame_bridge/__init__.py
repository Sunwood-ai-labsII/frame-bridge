"""
Frame Bridge - AI-powered video frame bridging application
2つの動画を最適なフレームで自動結合するAIアプリケーション
"""

__version__ = "1.0.0"
__author__ = "Sunwood AI Labs"
__email__ = "info@sunwood-ai-labs.com"

from .video_processor import VideoProcessor, FrameBridge
from .batch_processor import BatchProcessor

__all__ = [
    "VideoProcessor",
    "FrameBridge", 
    "BatchProcessor",
    "__version__",
    "__author__",
    "__email__"
]