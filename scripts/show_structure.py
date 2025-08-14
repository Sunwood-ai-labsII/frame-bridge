"""
Frame Bridge - Project Structure Display
プロジェクト構造を表示するスクリプト
"""

import os
from pathlib import Path

def show_tree(directory, prefix="", max_depth=3, current_depth=0):
    """ディレクトリツリーを表示"""
    if current_depth > max_depth:
        return
    
    directory = Path(directory)
    if not directory.exists():
        return
    
    items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if item.is_dir():
            print(f"{prefix}{current_prefix}{item.name}/")
            extension = "    " if is_last else "│   "
            show_tree(item, prefix + extension, max_depth, current_depth + 1)
        else:
            print(f"{prefix}{current_prefix}{item.name}")

def main():
    """メイン処理"""
    print("🎬 Frame Bridge - プロジェクト構造")
    print("=" * 60)
    
    # プロジェクトルートから表示
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("📁 プロジェクト構造:")
    print("frame-bridge/")
    show_tree(".", max_depth=3)
    
    print("\n" + "=" * 60)
    print("📊 主要コンポーネント:")
    print("• src/frame_bridge/     - メインライブラリ")
    print("• scripts/              - 実行スクリプト")
    print("• tests/                - テストファイル")
    print("• examples/             - サンプルデータ")
    print("• docs/                 - ドキュメント")
    
    print("\n🎯 新機能:")
    print("• エッジフレーム除外オプション")
    print("• 最適化されたフォルダ構造")
    print("• 設定管理システム")

if __name__ == "__main__":
    main()