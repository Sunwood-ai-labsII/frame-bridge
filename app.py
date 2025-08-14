import gradio as gr
from theme import create_zen_theme
from src.frame_bridge import BatchProcessor
import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path
from loguru import logger
from typing import List

# Batch Processor インスタンスを作成
batch_processor = BatchProcessor()

def process_uploaded_videos(video_files: List, mode: str, filename: str, progress=gr.Progress()):
    """アップロードされた動画ファイルをバッチ処理する関数"""
    if not video_files or len(video_files) < 2:
        return "最低2つの動画ファイルをアップロードしてください。", None, None
    
    try:
        progress(0.1, "動画ファイルを準備中...")
        
        # 一時ディレクトリを作成
        temp_input_dir = tempfile.mkdtemp(prefix="frame_bridge_input_")
        temp_output_dir = tempfile.mkdtemp(prefix="frame_bridge_output_")
        
        # アップロードされたファイルを一時ディレクトリにコピー
        for i, video_file in enumerate(video_files):
            if video_file is not None:
                file_extension = os.path.splitext(video_file.name)[1]
                temp_filename = f"video_{i:03d}{file_extension}"
                temp_path = os.path.join(temp_input_dir, temp_filename)
                shutil.copy2(video_file.name, temp_path)
        
        progress(0.3, "バッチプロセッサを初期化中...")
        
        # バッチプロセッサを初期化
        processor = BatchProcessor(output_dir=temp_output_dir)
        
        progress(0.5, f"{mode}処理を実行中...")
        
        if mode == "順次結合":
            success, final_output, results = processor.process_sequential_merge(
                temp_input_dir, 
                filename or "merged_sequence.mp4"
            )
            
            if success:
                progress(0.9, "レポート生成中...")
                report = processor.generate_report(results)
                
                # 結果ファイルをダウンロード可能な場所にコピー
                download_path = os.path.join(tempfile.gettempdir(), os.path.basename(final_output))
                shutil.copy2(final_output, download_path)
                
                progress(1.0, "完了！")
                return f"✅ 順次結合完了!\n📁 出力ファイル: {os.path.basename(final_output)}\n\n{report}", download_path, report
            else:
                return "❌ 順次結合に失敗しました", None, None
        
        elif mode == "ペア結合":
            success, output_files, results = processor.process_pairwise_merge(temp_input_dir)
            
            if success:
                progress(0.9, "レポート生成中...")
                report = processor.generate_report(results)
                
                # 最初の出力ファイルをダウンロード用にコピー
                if output_files:
                    download_path = os.path.join(tempfile.gettempdir(), os.path.basename(output_files[0]))
                    shutil.copy2(output_files[0], download_path)
                else:
                    download_path = None
                
                progress(1.0, "完了！")
                return f"✅ ペア結合完了!\n📁 出力ファイル数: {len(output_files)}\n\n{report}", download_path, report
            else:
                return "❌ ペア結合に失敗しました", None, None
    
    except Exception as e:
        return f"処理エラー: {str(e)}", None, None
    
    finally:
        # 一時ディレクトリをクリーンアップ
        try:
            shutil.rmtree(temp_input_dir, ignore_errors=True)
            shutil.rmtree(temp_output_dir, ignore_errors=True)
        except:
            pass

def get_video_info(video_files: List):
    """アップロードされた動画ファイルの情報を取得"""
    if not video_files:
        return "動画ファイルをアップロードしてください。"
    
    info_lines = [f"📊 アップロードされた動画: {len(video_files)}個\n"]
    
    for i, video_file in enumerate(video_files):
        if video_file is not None:
            try:
                file_size = os.path.getsize(video_file.name) / (1024 * 1024)  # MB
                info_lines.append(f"📹 動画{i+1}: {os.path.basename(video_file.name)}")
                info_lines.append(f"   📊 サイズ: {file_size:.1f} MB")
                info_lines.append("")
            except:
                info_lines.append(f"📹 動画{i+1}: {os.path.basename(video_file.name)} (情報取得エラー)")
                info_lines.append("")
    
    return "\n".join(info_lines)

# Gradioインターフェースの作成
def create_interface():
    """Gradioインターフェースを作成する関数"""
    theme = create_zen_theme()
    
    with gr.Blocks(theme=theme, title="Frame Bridge - バッチ動画結合アプリ") as demo:
        # ヘッダー
        gr.HTML("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #d4a574 0%, #ffffff 50%, #f5f2ed 100%); color: #3d405b; border-radius: 12px;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>🎬 Frame Bridge</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>複数動画を最適なフレームで自動結合するAIバッチ処理アプリ</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📹 動画ファイルアップロード")
                
                video_files = gr.File(
                    label="🎥 動画ファイル（複数選択可）",
                    file_count="multiple",
                    file_types=["video"],
                    height=200
                )
                
                video_info = gr.Textbox(
                    label="📊 アップロードされた動画情報",
                    lines=8,
                    interactive=False
                )
                
                gr.Markdown("### ⚙️ 処理設定")
                
                processing_mode = gr.Radio(
                    label="🔄 処理モード",
                    choices=["順次結合", "ペア結合"],
                    value="順次結合",
                    info="順次結合: 全動画を1つに結合 / ペア結合: 2つずつペアで結合"
                )
                
                output_filename = gr.Textbox(
                    label="📄 出力ファイル名 (順次結合のみ)",
                    placeholder="merged_sequence.mp4",
                    value="merged_sequence.mp4"
                )
                
                process_btn = gr.Button(
                    "🚀 バッチ処理実行", 
                    variant="primary", 
                    size="lg"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 処理結果")
                
                result_text = gr.Textbox(
                    label="📝 処理結果",
                    lines=15,
                    show_copy_button=True
                )
                
                output_video = gr.Video(
                    label="🎬 出力動画（プレビュー）",
                    height=300
                )
                
                report_text = gr.Textbox(
                    label="📋 詳細レポート",
                    lines=10,
                    show_copy_button=True
                )
        
        # 動画情報の自動更新
        video_files.change(
            fn=get_video_info,
            inputs=video_files,
            outputs=video_info
        )
        
        # バッチ処理実行
        process_btn.click(
            fn=process_uploaded_videos,
            inputs=[video_files, processing_mode, output_filename],
            outputs=[result_text, output_video, report_text]
        )
        
        # 使用方法の説明
        gr.Markdown("---")
        gr.Markdown("### 🎯 使用方法")
        gr.Markdown("1. **動画ファイルアップロード**: 結合したい動画ファイルを複数選択してアップロード")
        gr.Markdown("2. **処理モード選択**:")
        gr.Markdown("   - **順次結合**: アップロードした全動画を名前順に1つの動画に結合")
        gr.Markdown("   - **ペア結合**: 動画を2つずつペアにして結合（複数の出力ファイル）")
        gr.Markdown("3. **出力ファイル名**: 順次結合の場合の最終ファイル名を指定")
        gr.Markdown("4. **バッチ処理実行**: 設定した内容で一括処理を開始")
        
        gr.Markdown("### 🔬 技術的特徴")
        gr.Markdown("- **SSIM（構造的類似性指標）**: フレーム間の視覚的類似度を高精度で計算")
        gr.Markdown("- **自動最適化**: 動画間の最適な接続点を自動検出")
        gr.Markdown("- **バッチ処理**: 複数動画の自動処理とレポート生成")
        gr.Markdown("- **ファイルアップロード**: ローカルファイルを直接アップロードして処理")
        
        # ZENテーマの説明
        gr.HTML("""
        <div style='text-align: center; margin-top: 2rem; padding: 1.5rem; background: #ffffff; border-radius: 12px;'>
            <h3 style='color: #3d405b; margin-top: 0;'>🧘‍♀️ ZENテーマ</h3>
            <p style='color: #8b7355;'>和モダンなデザインで、直感的なバッチ動画処理体験を提供</p>
            <p style='color: #8b7355; font-size: 0.9rem;'>複数動画の一括処理に特化した高機能動画結合アプリ</p>
        </div>
        """)
    
    return demo

def run_cli_mode():
    """コマンドライン実行モード"""
    # loguruの設定
    logger.remove()  # デフォルトハンドラを削除
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")
    
    parser = argparse.ArgumentParser(description="Frame Bridge - AIバッチ動画結合アプリ")
    parser.add_argument("--input", "-i", help="入力フォルダ (バッチ処理用)")
    parser.add_argument("--output", "-o", default="output", help="出力フォルダ (デフォルト: output)")
    parser.add_argument("--mode", "-m", choices=["sequential", "pairwise"], default="sequential", 
                       help="結合モード: sequential(順次結合) または pairwise(ペア結合)")
    parser.add_argument("--filename", "-f", default="merged_sequence.mp4", help="出力ファイル名 (sequentialモードのみ)")
    parser.add_argument("--gui", action="store_true", help="GUIモードで起動")
    
    args = parser.parse_args()
    
    # GUIモードまたは引数なしの場合はGradioを起動
    if args.gui or not args.input:
        logger.info("🎬 Frame Bridge - GUI モードで起動")
        demo = create_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )
        return
    
    # バッチ処理モード
    logger.info("🎬 Frame Bridge - バッチ処理モード")
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
    
    # バッチプロセッサを初期化
    logger.info("🔧 バッチプロセッサを初期化中...")
    processor = BatchProcessor(output_dir=args.output)
    
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
        success, final_output, results = processor.process_sequential_merge(args.input, args.filename)
        
        if success:
            logger.success("✅ 順次結合完了!")
            logger.info(f"📁 最終出力: {final_output}")
            logger.info(f"📊 ファイルサイズ: {os.path.getsize(final_output) / (1024*1024):.1f} MB")
        else:
            logger.error("❌ 順次結合に失敗しました")
    
    elif args.mode == "pairwise":
        logger.info("🔄 ペアワイズ結合処理を開始...")
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

def main():
    """メイン関数 - pyproject.tomlのscriptsから呼び出される"""
    run_cli_mode()

if __name__ == "__main__":
    run_cli_mode()