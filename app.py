import gradio as gr
from theme import create_zen_theme
from src.frame_bridge import FrameBridge, BatchProcessor
import os

# Frame Bridge インスタンスを作成
frame_bridge = FrameBridge(exclude_edge_frames=True)
batch_processor = BatchProcessor(exclude_edge_frames=True)

def process_sample_videos():
    """サンプル動画を処理する関数"""
    video1_path = "examples/assets/example/REI/input/REI-001.mp4"
    video2_path = "examples/assets/example/REI/input/REI-002.mp4"
    
    if not os.path.exists(video1_path) or not os.path.exists(video2_path):
        return "サンプル動画ファイルが見つかりません。", None, None, None, 0.0
    
    return frame_bridge.process_video_bridge(video1_path, video2_path)

def process_batch_videos(input_folder, output_folder, mode, filename):
    """バッチ動画処理関数"""
    if not input_folder or not os.path.exists(input_folder):
        return "入力フォルダが指定されていないか、存在しません。", None
    
    if not output_folder:
        output_folder = "output"
    
    try:
        # バッチプロセッサを初期化
        processor = BatchProcessor(output_dir=output_folder, exclude_edge_frames=True)
        
        if mode == "順次結合":
            success, final_output, results = processor.process_sequential_merge(input_folder, filename or "merged_sequence.mp4")
            if success:
                report = processor.generate_report(results)
                return f"✅ 順次結合完了!\n📁 出力: {final_output}\n\n{report}", final_output
            else:
                return "❌ 順次結合に失敗しました", None
        
        elif mode == "ペア結合":
            success, output_files, results = processor.process_pairwise_merge(input_folder)
            if success:
                report = processor.generate_report(results)
                # 最初の出力ファイルを返す（複数ある場合）
                first_output = output_files[0] if output_files else None
                return f"✅ ペア結合完了!\n📁 出力ファイル数: {len(output_files)}\n\n{report}", first_output
            else:
                return "❌ ペア結合に失敗しました", None
    
    except Exception as e:
        return f"処理エラー: {str(e)}", None

def process_video_bridge(video1, video2, progress=gr.Progress()):
    """2つの動画を分析して最適な結合点を見つけ、結合する関数"""
    if video1 is None or video2 is None:
        return "2つの動画ファイルをアップロードしてください。", None, None, None, None
    
    try:
        progress(0.1, "動画を分析中...")
        
        result_text, output_path, frame1_path, frame2_path, similarity = frame_bridge.process_video_bridge(video1, video2)
        
        progress(1.0, "完了！")
        
        return result_text, output_path, frame1_path, frame2_path, similarity
        
    except Exception as e:
        return f"処理エラー: {str(e)}", None, None, None, None

def analyze_video_details(video_path):
    """動画の詳細情報を分析する関数"""
    if video_path is None:
        return ""
    return frame_bridge.processor.analyze_video_details(video_path)

# Gradioインターフェースの作成
def create_interface():
    """Gradioインターフェースを作成する関数"""
    theme = create_zen_theme()
    
    with gr.Blocks(theme=theme, title="Frame Bridge - 動画フレーム結合アプリ") as demo:
        # ヘッダー
        gr.HTML("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #d4a574 0%, #ffffff 50%, #f5f2ed 100%); color: #3d405b; border-radius: 12px;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>🎬 Frame Bridge</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>2つの動画を最適なフレームで自動結合するAIアプリ</p>
        </div>
        """)
        
        # タブの作成
        with gr.Tabs():
            # 単体処理タブ
            with gr.TabItem("🎥 単体処理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📹 動画アップロード")
                        video1_input = gr.Video(
                            label="🎥 動画1（前半）",
                            height=300
                        )
                        video1_info = gr.Textbox(
                            label="📊 動画1の情報",
                            lines=6,
                            interactive=False
                        )
                        
                        video2_input = gr.Video(
                            label="🎥 動画2（後半）",
                            height=300
                        )
                        video2_info = gr.Textbox(
                            label="📊 動画2の情報",
                            lines=6,
                            interactive=False
                        )
                        
                        bridge_btn = gr.Button("🌉 フレームブリッジ実行", variant="primary", size="lg")
                        sample_btn = gr.Button("🎬 サンプル動画で試す", variant="secondary", size="lg")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 結合結果")
                        result_text = gr.Textbox(
                            label="📝 分析結果",
                            lines=10,
                            show_copy_button=True
                        )
                        
                        merged_video = gr.Video(
                            label="🎬 結合された動画",
                            height=300
                        )
                        
                        # 接続フレーム表示
                        with gr.Row():
                            connection_frame1 = gr.Image(
                                label="🔗 動画1の接続フレーム",
                                height=200
                            )
                            connection_frame2 = gr.Image(
                                label="🔗 動画2の接続フレーム", 
                                height=200
                            )
                        
                        similarity_score = gr.Number(
                            label="📈 フレーム類似度スコア",
                            precision=3
                        )
            
            # バッチ処理タブ
            with gr.TabItem("📁 バッチ処理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📂 フォルダ指定")
                        input_folder = gr.Textbox(
                            label="📥 入力フォルダパス",
                            placeholder="例: examples/assets/example/REI/input",
                            value="examples/assets/example/REI/input"
                        )
                        output_folder = gr.Textbox(
                            label="📤 出力フォルダパス",
                            placeholder="例: examples/assets/example/REI/output",
                            value="examples/assets/example/REI/output"
                        )
                        
                        processing_mode = gr.Radio(
                            label="🔄 処理モード",
                            choices=["順次結合", "ペア結合"],
                            value="順次結合",
                            info="順次結合: 全動画を1つに結合 / ペア結合: 2つずつペアで結合"
                        )
                        
                        output_filename = gr.Textbox(
                            label="📄 出力ファイル名 (順次結合のみ)",
                            placeholder="REI_merged_sequence.mp4",
                            value="REI_merged_sequence.mp4"
                        )
                        
                        batch_btn = gr.Button("🚀 バッチ処理実行", variant="primary", size="lg")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 処理結果")
                        batch_result = gr.Textbox(
                            label="📝 バッチ処理結果",
                            lines=15,
                            show_copy_button=True
                        )
                        
                        batch_output = gr.Video(
                            label="🎬 出力動画（プレビュー）",
                            height=300
                        )

        
                # 動画情報の自動更新
                def update_video1_info(video):
                    if video is None:
                        return ""
                    return analyze_video_details(video)
                
                def update_video2_info(video):
                    if video is None:
                        return ""
                    return analyze_video_details(video)
                
                video1_input.change(
                    fn=update_video1_info,
                    inputs=video1_input,
                    outputs=video1_info
                )
                
                video2_input.change(
                    fn=update_video2_info,
                    inputs=video2_input,
                    outputs=video2_info
                )
                
                # メイン処理
                bridge_btn.click(
                    fn=process_video_bridge,
                    inputs=[video1_input, video2_input],
                    outputs=[result_text, merged_video, connection_frame1, connection_frame2, similarity_score]
                )
                
                # サンプル動画処理
                sample_btn.click(
                    fn=process_sample_videos,
                    inputs=[],
                    outputs=[result_text, merged_video, connection_frame1, connection_frame2, similarity_score]
                )
                
                # バッチ処理
                batch_btn.click(
                    fn=process_batch_videos,
                    inputs=[input_folder, output_folder, processing_mode, output_filename],
                    outputs=[batch_result, batch_output]
                )
        
        # 使用方法の説明
        gr.Markdown("---")
        gr.Markdown("### 🎯 使用方法")
        
        with gr.Tabs():
            with gr.TabItem("🎥 単体処理"):
                gr.Markdown("1. **動画1（前半）**: 結合したい最初の動画をアップロード")
                gr.Markdown("2. **動画2（後半）**: 結合したい2番目の動画をアップロード")
                gr.Markdown("3. **フレームブリッジ実行**: AIが最適な接続点を自動検出して結合")
                gr.Markdown("4. **サンプル動画で試す**: assetsフォルダのサンプル動画で機能をテスト")
            
            with gr.TabItem("📁 バッチ処理"):
                gr.Markdown("1. **入力フォルダ**: 動画ファイルが格納されたフォルダパスを指定")
                gr.Markdown("2. **出力フォルダ**: 結合結果を保存するフォルダパスを指定")
                gr.Markdown("3. **処理モード選択**:")
                gr.Markdown("   - **順次結合**: フォルダ内の全動画を名前順に1つの動画に結合")
                gr.Markdown("   - **ペア結合**: 動画を2つずつペアにして結合（複数の出力ファイル）")
                gr.Markdown("4. **出力ファイル名**: 順次結合の場合の最終ファイル名を指定")
                gr.Markdown("5. **バッチ処理実行**: 指定した設定で一括処理を開始")
        
        gr.Markdown("### 🔬 技術的特徴")
        gr.Markdown("- **SSIM（構造的類似性指標）**: フレーム間の視覚的類似度を高精度で計算")
        gr.Markdown("- **自動最適化**: 動画1の終了部分と動画2の開始部分から最適な接続点を検出")
        gr.Markdown("- **スムーズな結合**: 視覚的に自然な動画結合を実現")
        gr.Markdown("- **バッチ処理**: 複数動画の自動処理とレポート生成")
        gr.Markdown("- **ファイル名ソート**: 自然順序でのファイル名ソートによる正確な順序処理")
        
        # ZENテーマの説明
        gr.HTML("""
        <div style='text-align: center; margin-top: 2rem; padding: 1.5rem; background: #ffffff; border-radius: 12px;'>
            <h3 style='color: #3d405b; margin-top: 0;'>🧘‍♀️ ZENテーマ</h3>
            <p style='color: #8b7355;'>和モダンなデザインで、直感的な動画編集体験を提供</p>
            <p style='color: #8b7355; font-size: 0.9rem;'>単体処理とバッチ処理の両方に対応した高機能動画結合アプリ</p>
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    # インターフェースを作成
    demo = create_interface()
    
    # アプリケーションを実行
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
