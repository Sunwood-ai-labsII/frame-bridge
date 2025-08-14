"""
Frame Bridge - バッチ処理テスト用スクリプト
フォルダ内の動画ファイルを順次結合するテストスクリプト
"""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger
import sys
sys.path.append('..')
from src.frame_bridge import BatchProcessor

# loguruの設定
logger.remove()  # デフォルトハンドラを削除
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Frame Bridge - バッチ動画結合")
    parser.add_argument("--input", "-i", default="assets/example/REI/input", help="入力フォルダ (デフォルト: examples/assets/example/REI/input)")
    parser.add_argument("--output", "-o", default="assets/example/REI/output", help="出力フォルダ (デフォルト: examples/assets/example/REI/output)")
    parser.add_argument("--exclude-edge", action="store_true", default=True, help="最初と最後のフレームを除外 (デフォルト: True)")
    parser.add_argument("--include-edge", action="store_true", help="最初と最後のフレームを含める")
    parser.add_argument("--mode", "-m", choices=["sequential", "pairwise"], default="sequential", 
                       help="結合モード: sequential(順次結合) または pairwise(ペア結合)")
    parser.add_argument("--filename", "-f", default="merged_sequence.mp4", help="出力ファイル名 (sequentialモードのみ)")
    
    args = parser.parse_args()
    
    logger.info("🎬 Frame Bridge - バッチ処理テスト開始")
    logger.info("=" * 60)
    logger.info(f"📁 入力フォルダ: {args.input}")
    logger.info(f"📁 出力フォルダ: {args.output}")
    logger.info(f"🔄 処理モード: {args.mode}")
    if args.mode == "sequential":
        logger.info(f"📄 出力ファイル名: {args.filename}")
    
    # 入力フォルダの存在チェック
    if not os.path.exists(args.input):
        logger.error(f"❌ 入力フォルダが見つかりません: {args.input}")
        return
    
    # エッジフレーム除外設定
    exclude_edge_frames = not args.include_edge if args.include_edge else args.exclude_edge
    
    logger.info(f"🎯 エッジフレーム除外: {'有効' if exclude_edge_frames else '無効'}")
    
    # バッチプロセッサを初期化
    logger.info("🔧 バッチプロセッサを初期化中...")
    processor = BatchProcessor(output_dir=args.output, exclude_edge_frames=exclude_edge_frames)
    
    # 動画ファイルの確認
    logger.info("📂 動画ファイルをスキャン中...")
    video_files = processor.get_video_files(args.input)
    if len(video_files) < 2:
        logger.error("❌ 結合には最低2つの動画ファイルが必要です")
        return
    
    logger.success(f"✅ 検出された動画ファイル: {len(video_files)}個")
    for i, file in enumerate(video_files):
        logger.info(f"  {i+1}. {os.path.basename(file)}")
    
    # 処理モードに応じて実行
    if args.mode == "sequential":
        logger.info("🔄 順次結合処理を開始...")
        with logger.contextualize(task="sequential_merge"):
            success, final_output, results = processor.process_sequential_merge(args.input, args.filename)
        
        if success:
            logger.success("✅ 順次結合完了!")
            logger.info(f"📁 最終出力: {final_output}")
            logger.info(f"📊 ファイルサイズ: {os.path.getsize(final_output) / (1024*1024):.1f} MB")
        else:
            logger.error("❌ 順次結合に失敗しました")
    
    elif args.mode == "pairwise":
        logger.info("🔄 ペアワイズ結合処理を開始...")
        with logger.contextualize(task="pairwise_merge"):
            success, output_files, results = processor.process_pairwise_merge(args.input)
        
        if success:
            logger.success("✅ ペアワイズ結合完了!")
            logger.info(f"📁 出力ファイル数: {len(output_files)}")
            for i, file in enumerate(output_files):
                size_mb = os.path.getsize(file) / (1024*1024)
                logger.info(f"  {i+1}. {os.path.basename(file)} ({size_mb:.1f} MB)")
        else:
            logger.error("❌ ペアワイズ結合に失敗しました")
    
    # レポート生成
    logger.info("=" * 60)
    logger.info("📋 処理レポート生成中...")
    report_path = Path(args.output) / "batch_report.txt"
    report = processor.generate_report(results, str(report_path))
    print(report)  # レポートは通常のprintで表示
    
    logger.success("🎉 バッチ処理完了！")

if __name__ == "__main__":
    main()