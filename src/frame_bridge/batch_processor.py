"""
Frame Bridge - Batch Processing Module
フォルダ内の動画ファイルを順次結合するバッチ処理モジュール
"""

import os
import glob
from pathlib import Path
from typing import List, Tuple, Optional
from loguru import logger
from .video_processor import FrameBridge


class BatchProcessor:
    """バッチ処理を行うクラス"""
    
    def __init__(self, output_dir: str = "output"):
        """
        初期化
        
        Args:
            output_dir: 出力ディレクトリ
        """
        self.frame_bridge = FrameBridge()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # サポートする動画形式
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    def get_video_files(self, input_dir: str) -> List[str]:
        """
        指定ディレクトリから動画ファイルを取得し、名前順にソート
        
        Args:
            input_dir: 入力ディレクトリ
            
        Returns:
            ソートされた動画ファイルのリスト
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"入力ディレクトリが存在しません: {input_dir}")
            return []
        
        video_files = []
        for ext in self.supported_formats:
            pattern = str(input_path / f"*{ext}")
            video_files.extend(glob.glob(pattern))
        
        # ファイル名でソート（自然順序）
        video_files.sort(key=lambda x: os.path.basename(x).lower())
        
        logger.info(f"検出された動画ファイル数: {len(video_files)}")
        for i, file in enumerate(video_files):
            logger.info(f"  {i+1}. {os.path.basename(file)}")
        
        return video_files
    
    def process_sequential_merge(self, input_dir: str, output_filename: str = "merged_sequence.mp4") -> Tuple[bool, str, List[dict]]:
        """
        フォルダ内の動画を順次結合
        
        Args:
            input_dir: 入力ディレクトリ
            output_filename: 出力ファイル名
            
        Returns:
            Tuple[成功フラグ, 最終出力パス, 処理結果リスト]
        """
        video_files = self.get_video_files(input_dir)
        
        if len(video_files) < 2:
            return False, "", [{"error": "結合には最低2つの動画ファイルが必要です"}]
        
        results = []
        current_video = video_files[0]
        
        logger.info(f"順次結合処理開始: {len(video_files)}個のファイル")
        
        for i in range(1, len(video_files)):
            next_video = video_files[i]
            
            logger.info(f"結合 {i}/{len(video_files)-1}: {os.path.basename(current_video)} + {os.path.basename(next_video)}")
            
            # 中間出力ファイル名
            if i == len(video_files) - 1:
                # 最後の結合は最終ファイル名
                temp_output = self.output_dir / output_filename
            else:
                # 中間ファイル
                temp_output = self.output_dir / f"temp_merge_{i}.mp4"
            
            # 結合処理
            result_text, output_path, frame1_path, frame2_path, similarity = self.frame_bridge.process_video_bridge(
                current_video, next_video
            )
            
            if output_path and os.path.exists(output_path):
                # 結果を指定の場所に移動
                import shutil
                shutil.move(output_path, str(temp_output))
                
                result_info = {
                    "step": i,
                    "video1": os.path.basename(current_video),
                    "video2": os.path.basename(next_video),
                    "similarity": similarity,
                    "output": str(temp_output),
                    "success": True
                }
                
                # 次のループでは結合結果を使用
                current_video = str(temp_output)
                
                logger.info(f"結合完了 {i}/{len(video_files)-1}: 類似度 {similarity:.3f}")
            else:
                result_info = {
                    "step": i,
                    "video1": os.path.basename(current_video),
                    "video2": os.path.basename(next_video),
                    "error": result_text,
                    "success": False
                }
                logger.error(f"結合失敗 {i}/{len(video_files)-1}: {result_text}")
            
            results.append(result_info)
            
            # 中間ファイルのクリーンアップ（最後以外）
            if i > 1 and i < len(video_files) - 1:
                prev_temp = self.output_dir / f"temp_merge_{i-1}.mp4"
                if prev_temp.exists():
                    prev_temp.unlink()
        
        final_output = self.output_dir / output_filename
        success = final_output.exists()
        
        if success:
            logger.info(f"全結合処理完了: {final_output}")
            logger.info(f"最終ファイルサイズ: {final_output.stat().st_size / (1024*1024):.1f} MB")
        
        return success, str(final_output), results
    
    def process_pairwise_merge(self, input_dir: str) -> Tuple[bool, List[str], List[dict]]:
        """
        フォルダ内の動画をペアワイズで結合
        
        Args:
            input_dir: 入力ディレクトリ
            
        Returns:
            Tuple[成功フラグ, 出力ファイルリスト, 処理結果リスト]
        """
        video_files = self.get_video_files(input_dir)
        
        if len(video_files) < 2:
            return False, [], [{"error": "結合には最低2つの動画ファイルが必要です"}]
        
        results = []
        output_files = []
        
        logger.info(f"ペアワイズ結合処理開始: {len(video_files)}個のファイル")
        
        # ペアごとに処理
        for i in range(0, len(video_files) - 1, 2):
            video1 = video_files[i]
            video2 = video_files[i + 1] if i + 1 < len(video_files) else None
            
            if video2 is None:
                # 奇数個の場合、最後のファイルはそのままコピー
                import shutil
                output_name = f"single_{os.path.basename(video1)}"
                output_path = self.output_dir / output_name
                shutil.copy2(video1, output_path)
                output_files.append(str(output_path))
                
                results.append({
                    "pair": i // 2 + 1,
                    "video1": os.path.basename(video1),
                    "video2": None,
                    "action": "copied",
                    "output": str(output_path),
                    "success": True
                })
                continue
            
            logger.info(f"ペア {i//2 + 1}: {os.path.basename(video1)} + {os.path.basename(video2)}")
            
            # 出力ファイル名
            output_name = f"merged_pair_{i//2 + 1}_{os.path.basename(video1).split('.')[0]}_{os.path.basename(video2).split('.')[0]}.mp4"
            output_path = self.output_dir / output_name
            
            # 結合処理
            result_text, temp_output, frame1_path, frame2_path, similarity = self.frame_bridge.process_video_bridge(
                video1, video2
            )
            
            if temp_output and os.path.exists(temp_output):
                # 結果を指定の場所に移動
                import shutil
                shutil.move(temp_output, str(output_path))
                output_files.append(str(output_path))
                
                result_info = {
                    "pair": i // 2 + 1,
                    "video1": os.path.basename(video1),
                    "video2": os.path.basename(video2),
                    "similarity": similarity,
                    "output": str(output_path),
                    "success": True
                }
                
                logger.info(f"ペア結合完了 {i//2 + 1}: 類似度 {similarity:.3f}")
            else:
                result_info = {
                    "pair": i // 2 + 1,
                    "video1": os.path.basename(video1),
                    "video2": os.path.basename(video2),
                    "error": result_text,
                    "success": False
                }
                logger.error(f"ペア結合失敗 {i//2 + 1}: {result_text}")
            
            results.append(result_info)
        
        success = len(output_files) > 0
        logger.info(f"ペアワイズ結合完了: {len(output_files)}個のファイル出力")
        
        return success, output_files, results
    
    def generate_report(self, results: List[dict], output_path: str = None) -> str:
        """
        処理結果のレポートを生成
        
        Args:
            results: 処理結果リスト
            output_path: レポート出力パス
            
        Returns:
            レポート文字列
        """
        report_lines = [
            "🎬 Frame Bridge - バッチ処理レポート",
            "=" * 60,
            f"📅 処理日時: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 総処理数: {len(results)}",
            ""
        ]
        
        success_count = sum(1 for r in results if r.get('success', False))
        report_lines.extend([
            f"✅ 成功: {success_count}",
            f"❌ 失敗: {len(results) - success_count}",
            ""
        ])
        
        # 詳細結果
        for i, result in enumerate(results, 1):
            if result.get('success', False):
                if 'similarity' in result:
                    quality = self._evaluate_quality(result['similarity'])
                    report_lines.extend([
                        f"📋 処理 {i}: ✅ 成功",
                        f"   📹 動画1: {result.get('video1', 'N/A')}",
                        f"   📹 動画2: {result.get('video2', 'N/A')}",
                        f"   📈 類似度: {result['similarity']:.3f} ({quality})",
                        f"   📁 出力: {os.path.basename(result.get('output', 'N/A'))}",
                        ""
                    ])
                else:
                    report_lines.extend([
                        f"📋 処理 {i}: ✅ {result.get('action', '処理完了')}",
                        f"   📹 ファイル: {result.get('video1', 'N/A')}",
                        f"   📁 出力: {os.path.basename(result.get('output', 'N/A'))}",
                        ""
                    ])
            else:
                report_lines.extend([
                    f"📋 処理 {i}: ❌ 失敗",
                    f"   📹 動画1: {result.get('video1', 'N/A')}",
                    f"   📹 動画2: {result.get('video2', 'N/A')}",
                    f"   ⚠️ エラー: {result.get('error', '不明なエラー')}",
                    ""
                ])
        
        report_text = "\n".join(report_lines)
        
        # ファイルに保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"レポート保存: {output_path}")
        
        return report_text
    
    def _evaluate_quality(self, similarity: float) -> str:
        """類似度から品質を評価"""
        if similarity > 0.8:
            return "優秀"
        elif similarity > 0.6:
            return "良好"
        elif similarity > 0.4:
            return "普通"
        else:
            return "要確認"