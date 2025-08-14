"""
Frame Bridge - バッチ処理テスト用スクリプト
フォルダ内の動画ファイルを順次結合するテストスクリプト
"""

import os
import sys
import argparse
from pathlib import Path
import sys
sys.path.append('..')
from src.frame_bridge import BatchProcessor

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Frame Bridge - バッチ動画結合")
    parser.add_argument("--input", "-i", default="examples/assets/example/REI/input", help="入力フォルダ (デフォルト: examples/assets/example/REI/input)")
    parser.add_argument("--output", "-o", default="examples/assets/example/REI/output", help="出力フォルダ (デフォルト: examples/assets/example/REI/output)")
    parser.add_argument("--exclude-edge", action="store_true", default=True, help="最初と最後のフレームを除外 (デフォルト: True)")
    parser.add_argument("--include-edge", action="store_true", help="最初と最後のフレームを含める")
    parser.add_argument("--mode", "-m", choices=["sequential", "pairwise"], default="sequential", 
                       help="結合モード: sequential(順次結合) または pairwise(ペア結合)")
    parser.add_argument("--filename", "-f", default="merged_sequence.mp4", help="出力ファイル名 (sequentialモードのみ)")
    
    args = parser.parse_args()
    
    print("🎬 Frame Bridge - バッチ処理テスト")
    print("=" * 60)
    print(f"📁 入力フォルダ: {args.input}")
    print(f"📁 出力フォルダ: {args.output}")
    print(f"🔄 処理モード: {args.mode}")
    if args.mode == "sequential":
        print(f"📄 出力ファイル名: {args.filename}")
    print()
    
    # 入力フォルダの存在チェック
    if not os.path.exists(args.input):
        print(f"❌ 入力フォルダが見つかりません: {args.input}")
        return
    
    # エッジフレーム除外設定
    exclude_edge_frames = not args.include_edge if args.include_edge else args.exclude_edge
    
    print(f"🎯 エッジフレーム除外: {'有効' if exclude_edge_frames else '無効'}")
    print()
    
    # バッチプロセッサを初期化
    processor = BatchProcessor(output_dir=args.output, exclude_edge_frames=exclude_edge_frames)
    
    # 動画ファイルの確認
    video_files = processor.get_video_files(args.input)
    if len(video_files) < 2:
        print("❌ 結合には最低2つの動画ファイルが必要です")
        return
    
    print(f"✅ 検出された動画ファイル: {len(video_files)}個")
    for i, file in enumerate(video_files):
        print(f"  {i+1}. {os.path.basename(file)}")
    print()
    
    # 処理モードに応じて実行
    if args.mode == "sequential":
        print("🔄 順次結合処理を開始...")
        success, final_output, results = processor.process_sequential_merge(args.input, args.filename)
        
        if success:
            print(f"✅ 順次結合完了!")
            print(f"📁 最終出力: {final_output}")
            print(f"📊 ファイルサイズ: {os.path.getsize(final_output) / (1024*1024):.1f} MB")
        else:
            print("❌ 順次結合に失敗しました")
    
    elif args.mode == "pairwise":
        print("🔄 ペアワイズ結合処理を開始...")
        success, output_files, results = processor.process_pairwise_merge(args.input)
        
        if success:
            print(f"✅ ペアワイズ結合完了!")
            print(f"📁 出力ファイル数: {len(output_files)}")
            for i, file in enumerate(output_files):
                size_mb = os.path.getsize(file) / (1024*1024)
                print(f"  {i+1}. {os.path.basename(file)} ({size_mb:.1f} MB)")
        else:
            print("❌ ペアワイズ結合に失敗しました")
    
    # レポート生成
    print("\n" + "=" * 60)
    print("📋 処理レポート:")
    report_path = Path(args.output) / "batch_report.txt"
    report = processor.generate_report(results, str(report_path))
    print(report)
    
    print("🎉 バッチ処理完了！")

if __name__ == "__main__":
    main()