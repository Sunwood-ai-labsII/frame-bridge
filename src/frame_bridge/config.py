"""
Frame Bridge - Configuration Module
設定管理モジュール
"""

from dataclasses import dataclass
from typing import List


@dataclass
class VideoProcessorConfig:
    """VideoProcessor設定クラス"""
    similarity_threshold: float = 0.3
    exclude_edge_frames: bool = True
    num_frames_video1: int = 30  # 動画1から抽出するフレーム数
    num_frames_video2: int = 10  # 動画2から抽出するフレーム数
    comparison_frames: int = 3   # 動画2の比較対象フレーム数


@dataclass
class BatchProcessorConfig:
    """BatchProcessor設定クラス"""
    output_dir: str = "output"
    exclude_edge_frames: bool = True
    supported_formats: List[str] = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']


@dataclass
class AppConfig:
    """アプリケーション全体設定クラス"""
    video_processor: VideoProcessorConfig = None
    batch_processor: BatchProcessorConfig = None
    
    def __post_init__(self):
        if self.video_processor is None:
            self.video_processor = VideoProcessorConfig()
        if self.batch_processor is None:
            self.batch_processor = BatchProcessorConfig()


# デフォルト設定
DEFAULT_CONFIG = AppConfig()