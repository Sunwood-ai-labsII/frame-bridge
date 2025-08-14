"""
Frame Bridge - サンプル動画テスト用スクリプト
指定されたサンプル動画でFrame Bridgeの機能をテストします
"""

import os
import sys
import sys
sys.path.append('..')
from src.frame_bridge import FrameBridge

def main():
    """メイン処理"""
    print("🎬 Frame Bridge - サンプル動画テスト")
    print("=" * 50)
    
    # サンプル動画のパス
    video1_path = "examples/assets/example/REI/input/REI-001.mp4"
    video2_path = "examples/assets/example/REI/input/REI-002.mp4"
    
    # ファイル存在チェック
    if not os.path.exists(video1_path):
        print(f"❌ 動画1が見つかりません: {video1_path}")
        return
    
    if not os.path.exists(video2_path):
        print(f"❌ 動画2が見つかりません: {video2_path}")
        return
    
    print(f"✅ 動画1: {video1_path}")
    print(f"✅ 動画2: {video2_path}")
    print()
    
    # Frame Bridge インスタンスを作成（エッジフレーム除外有効）
    frame_bridge = FrameBridge(exclude_edge_frames=True)
    print(f"🎯 エッジフレーム除外: 有効")
    
    # 動画情報を表示
    print("📊 動画1の詳細情報:")
    print(frame_bridge.processor.analyze_video_details(video1_path))
    print()
    
    print("📊 動画2の詳細情報:")
    print(frame_bridge.processor.analyze_video_details(video2_path))
    print()
    
    # フレーム結合処理を実行
    print("🔄 フレーム結合処理を開始...")
    result_text, output_path, frame1_path, frame2_path, similarity = frame_bridge.process_video_bridge(
        video1_path, video2_path
    )
    
    print("\n" + "=" * 50)
    print("📋 処理結果:")
    print(result_text)
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ 結合動画が作成されました: {output_path}")
        print(f"📁 ファイルサイズ: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    
    if frame1_path and os.path.exists(frame1_path):
        print(f"🖼️ 接続フレーム1: {frame1_path}")
    
    if frame2_path and os.path.exists(frame2_path):
        print(f"🖼️ 接続フレーム2: {frame2_path}")
    
    print(f"\n📈 最終類似度スコア: {similarity:.3f}")
    
    print("\n🎉 テスト完了！")

if __name__ == "__main__":
    main()