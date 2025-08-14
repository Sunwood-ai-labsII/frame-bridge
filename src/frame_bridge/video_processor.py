"""
Frame Bridge - Video Processing Module
2つの動画を最適なフレームで結合するための処理モジュール
"""

import cv2
import numpy as np
from PIL import Image
import tempfile
import os
from skimage.metrics import structural_similarity as ssim
from typing import Tuple, List, Optional, Union
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """動画処理を行うメインクラス"""
    
    def __init__(self, similarity_threshold: float = 0.3, exclude_edge_frames: bool = True):
        """
        初期化
        
        Args:
            similarity_threshold: フレーム類似度の閾値
            exclude_edge_frames: 最初と最後のフレームを除外するかどうか
        """
        self.similarity_threshold = similarity_threshold
        self.exclude_edge_frames = exclude_edge_frames
        
    def extract_frames(self, video_path: str, num_frames: int = 20) -> Tuple[Optional[List], Optional[str]]:
        """
        動画からフレームを抽出する
        
        Args:
            video_path: 動画ファイルのパス
            num_frames: 抽出するフレーム数
            
        Returns:
            Tuple[フレームリスト, エラーメッセージ]
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None, f"動画ファイルを開けませんでした: {video_path}"
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                return None, "動画にフレームが見つかりませんでした"
            
            logger.info(f"動画 {video_path}: 総フレーム数 {total_frames}")
            
            frames = []
            # 最初と最後のフレームを含む等間隔でフレームを抽出
            frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # BGR to RGB変換
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append((frame_idx, frame_rgb))
            
            cap.release()
            logger.info(f"フレーム抽出完了: {len(frames)}フレーム")
            return frames, None
            
        except Exception as e:
            logger.error(f"フレーム抽出エラー: {e}")
            return None, f"フレーム抽出エラー: {str(e)}"

    def calculate_frame_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        2つのフレーム間の類似度を計算する
        
        Args:
            frame1: 比較フレーム1
            frame2: 比較フレーム2
            
        Returns:
            類似度スコア (0.0-1.0)
        """
        try:
            # グレースケールに変換
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            
            # 同じサイズにリサイズ
            h, w = min(gray1.shape[0], gray2.shape[0]), min(gray1.shape[1], gray2.shape[1])
            gray1 = cv2.resize(gray1, (w, h))
            gray2 = cv2.resize(gray2, (w, h))
            
            # SSIM（構造的類似性指標）を計算
            similarity = ssim(gray1, gray2)
            return max(0.0, similarity)  # 負の値を0にクリップ
            
        except Exception as e:
            logger.error(f"類似度計算エラー: {e}")
            return 0.0

    def find_best_connection_frames(self, video1_path: str, video2_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], float, Optional[str], Tuple[int, int]]:
        """
        2つの動画の最適な接続フレームを見つける
        動画2の最初のフレームと動画1の全フレームから最も類似したフレームを探索
        
        Args:
            video1_path: 動画1のパス
            video2_path: 動画2のパス
            
        Returns:
            Tuple[最適フレーム1, 最適フレーム2, 類似度, エラーメッセージ, フレームインデックス]
        """
        try:
            # 各動画からフレームを抽出
            frames1, error1 = self.extract_frames(video1_path, 30)  # より多くのフレームを抽出
            if error1:
                return None, None, 0.0, error1, (0, 0)
            
            frames2, error2 = self.extract_frames(video2_path, 10)  # 動画2は少なめでOK
            if error2:
                return None, None, 0.0, error2, (0, 0)
            
            # エッジフレーム除外オプションの適用
            if self.exclude_edge_frames:
                # 最初と最後のフレームを除外
                frames1_filtered = frames1[1:-1] if len(frames1) > 2 else frames1
                frames2_filtered = frames2[1:-1] if len(frames2) > 2 else frames2
                logger.info(f"エッジフレーム除外: 動画1 {len(frames1)} → {len(frames1_filtered)}フレーム, 動画2 {len(frames2)} → {len(frames2_filtered)}フレーム")
            else:
                frames1_filtered = frames1
                frames2_filtered = frames2
                logger.info("エッジフレーム除外: 無効")
            
            # 動画2の最初の数フレームを基準にする（より高精度な探索）
            video2_start_frames = frames2_filtered[:3]  # 動画2の最初の3フレーム（エッジ除外後）
            
            best_similarity = -1
            best_frame1 = None
            best_frame2 = None
            best_indices = (0, 0)
            
            logger.info(f"フレーム類似度分析開始: 動画2の最初の{len(video2_start_frames)}フレームと動画1の{len(frames1_filtered)}フレームを比較...")
            
            # 動画2の各開始フレームについて、動画1の全フレームと比較
            for j, (idx2, frame2) in enumerate(video2_start_frames):
                logger.info(f"動画2のフレーム[{idx2}]との比較開始...")
                
                for i, (idx1, frame1) in enumerate(frames1_filtered):
                    similarity = self.calculate_frame_similarity(frame1, frame2)
                    logger.info(f"  動画1[{idx1}] vs 動画2[{idx2}]: 類似度 {similarity:.3f}")
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_frame1 = frame1
                        best_frame2 = frame2
                        best_indices = (idx1, idx2)
                        logger.info(f"  🌟 新しい最高類似度: {similarity:.3f} (動画1[{idx1}] → 動画2[{idx2}])")
            
            logger.info(f"最適接続点検出完了: 類似度 {best_similarity:.3f}")
            logger.info(f"最適結合点: 動画1のフレーム[{best_indices[0]}] → 動画2のフレーム[{best_indices[1]}]")
            
            return best_frame1, best_frame2, best_similarity, None, best_indices
            
        except Exception as e:
            logger.error(f"フレーム比較エラー: {e}")
            return None, None, 0.0, f"フレーム比較エラー: {str(e)}", (0, 0)

    def create_merged_video(self, video1_path: str, video2_path: str, cut_frame1: int, cut_frame2: int, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        2つの動画を指定されたフレームで結合する
        
        Args:
            video1_path: 動画1のパス
            video2_path: 動画2のパス
            cut_frame1: 動画1のカットフレーム
            cut_frame2: 動画2のカットフレーム
            output_path: 出力パス
            
        Returns:
            Tuple[成功フラグ, エラーメッセージ]
        """
        try:
            # 動画1を読み込み
            cap1 = cv2.VideoCapture(video1_path)
            if not cap1.isOpened():
                return False, "動画1を開けませんでした"
            
            # 動画2を読み込み
            cap2 = cv2.VideoCapture(video2_path)
            if not cap2.isOpened():
                cap1.release()
                return False, "動画2を開けませんでした"
            
            # 動画の情報を取得
            fps1 = cap1.get(cv2.CAP_PROP_FPS)
            width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"動画1情報: {width1}x{height1}, {fps1}fps")
            
            # 出力動画の設定（最初の動画の設定を使用）
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps1, (width1, height1))
            
            # 動画1の最初からcut_frame1まで
            frame_count = 0
            while frame_count <= cut_frame1:
                ret, frame = cap1.read()
                if not ret:
                    break
                out.write(frame)
                frame_count += 1
            
            logger.info(f"動画1から {frame_count} フレームを結合")
            
            # 動画2のcut_frame2から最後まで
            cap2.set(cv2.CAP_PROP_POS_FRAMES, cut_frame2)
            frame_count2 = 0
            while True:
                ret, frame = cap2.read()
                if not ret:
                    break
                # サイズを動画1に合わせる
                if frame.shape[:2] != (height1, width1):
                    frame = cv2.resize(frame, (width1, height1))
                out.write(frame)
                frame_count2 += 1
            
            logger.info(f"動画2から {frame_count2} フレームを結合")
            
            # リソースを解放
            cap1.release()
            cap2.release()
            out.release()
            
            logger.info(f"動画結合完了: {output_path}")
            return True, None
            
        except Exception as e:
            logger.error(f"動画結合エラー: {e}")
            return False, f"動画結合エラー: {str(e)}"

    def save_frame_as_image(self, frame: np.ndarray, filename: str) -> Optional[str]:
        """
        フレームを画像として保存する
        
        Args:
            frame: 保存するフレーム
            filename: ファイル名
            
        Returns:
            保存されたファイルのパス
        """
        try:
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            
            # PIL Imageに変換して保存
            pil_image = Image.fromarray(frame)
            pil_image.save(file_path)
            
            logger.info(f"フレーム画像保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"画像保存エラー: {e}")
            return None

    def analyze_video_details(self, video_path: str) -> str:
        """
        動画の詳細情報を分析する
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            動画情報の文字列
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return "動画を開けませんでした"
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return f"""📹 動画情報:
• 解像度: {width} x {height}
• フレームレート: {fps:.2f} FPS
• 総フレーム数: {frame_count}
• 再生時間: {duration:.2f} 秒
• ファイルサイズ: {os.path.getsize(video_path) / (1024*1024):.1f} MB"""
            
        except Exception as e:
            logger.error(f"動画分析エラー: {e}")
            return f"動画分析エラー: {str(e)}"


class FrameBridge:
    """Frame Bridge メインクラス"""
    
    def __init__(self, exclude_edge_frames: bool = True):
        """
        初期化
        
        Args:
            exclude_edge_frames: 最初と最後のフレームを除外するかどうか
        """
        self.processor = VideoProcessor(exclude_edge_frames=exclude_edge_frames)
    
    def process_video_bridge(self, video1_path: str, video2_path: str) -> Tuple[str, Optional[str], Optional[str], Optional[str], float]:
        """
        2つの動画を分析して最適な結合点を見つけ、結合する
        
        Args:
            video1_path: 動画1のパス
            video2_path: 動画2のパス
            
        Returns:
            Tuple[結果テキスト, 結合動画パス, フレーム1パス, フレーム2パス, 類似度]
        """
        if not video1_path or not video2_path:
            return "2つの動画ファイルが必要です。", None, None, None, 0.0
        
        if not os.path.exists(video1_path) or not os.path.exists(video2_path):
            return "指定された動画ファイルが見つかりません。", None, None, None, 0.0
        
        try:
            logger.info("動画分析開始...")
            
            # 最適な接続フレームを見つける
            frame1, frame2, similarity, error, indices = self.processor.find_best_connection_frames(video1_path, video2_path)
            
            if error:
                return f"エラー: {error}", None, None, None, 0.0
            
            logger.info("最適な接続点を検出しました")
            
            # フレームを画像として保存
            frame1_path = self.processor.save_frame_as_image(frame1, "connection_frame1.png")
            frame2_path = self.processor.save_frame_as_image(frame2, "connection_frame2.png")
            
            logger.info("動画結合開始...")
            
            # 結合動画を作成
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "merged_video.mp4")
            
            # 最適なフレームで結合
            success, merge_error = self.processor.create_merged_video(
                video1_path, video2_path, indices[0], indices[1], output_path
            )
            
            if not success:
                return f"動画結合エラー: {merge_error}", None, None, None, similarity
            
            # 品質評価
            quality = self._evaluate_quality(similarity)
            
            result_text = f"""🎬 動画結合完了！

📊 分析結果:
• フレーム類似度: {similarity:.3f}
• 接続品質: {quality}
• 結合フレーム: 動画1[{indices[0]}] → 動画2[{indices[1]}]

💡 結合情報:
• 動画1の最適な終了フレームを検出
• 動画2の最適な開始フレームを検出
• スムーズな接続を実現

📁 出力ファイル: {os.path.basename(output_path)}"""
            
            logger.info("処理完了")
            return result_text, output_path, frame1_path, frame2_path, similarity
            
        except Exception as e:
            logger.error(f"処理エラー: {e}")
            return f"処理エラー: {str(e)}", None, None, None, 0.0
    
    def _evaluate_quality(self, similarity: float) -> str:
        """類似度から品質を評価"""
        if similarity > 0.8:
            return "優秀 🌟"
        elif similarity > 0.6:
            return "良好 ✅"
        elif similarity > 0.4:
            return "普通 ⚡"
        else:
            return "要確認 ⚠️"