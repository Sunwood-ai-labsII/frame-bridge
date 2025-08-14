import requests
from bs4 import BeautifulSoup
import html2text
import re
import gradio as gr
from theme import create_zen_theme
import tempfile
import os
import zipfile
from urllib.parse import urlparse, unquote

def scrape_wikipedia_to_markdown_final(url: str) -> str:
    """
    Wikipediaページをスクレイピングし、整形・不要部分削除を行い、
    タイトルを付けてMarkdownに変換します。

    処理フロー：
    1. ページのタイトルをH1見出しとして取得します。
    2. 「登場人物」などの<dt>タグを見出しに変換します。
    3. 生成されたMarkdown文字列から「## 脚注」以降を完全に削除します。
    4. [編集]リンクを削除します。
    5. 最終的にタイトルと本文を結合して返します。

    Args:
        url (str): スクレイピング対象のWikipediaページのURL。

    Returns:
        str: 整形・変換された最終的なMarkdownコンテンツ。失敗した場合は空の文字列。
    """
    try:
        # 1. HTMLの取得と解析
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        response.encoding = response.apparent_encoding  # 文字コードを自動検出
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- ページのタイトルを取得 ---
        title_tag = soup.find('h1', id='firstHeading')
        page_title = title_tag.get_text(strip=True) if title_tag else "Wikipedia ページ"

        # 2. 主要コンテンツエリアの特定
        content_div = soup.find('div', class_='mw-parser-output')
        if not content_div:
            return "エラー: コンテンツエリアが見つかりませんでした。"

        # 3. HTMLの事前整形（登場人物などの見出し化）
        for dt_tag in content_div.find_all('dt'):
            h4_tag = soup.new_tag('h4')
            h4_tag.extend(dt_tag.contents)
            dt_tag.replace_with(h4_tag)

        # 4. HTMLからMarkdownへの一次変換
        h = html2text.HTML2Text()
        h.body_width = 0  # テキストの折り返しを無効にする
        full_markdown_text = h.handle(str(content_div))

        # 5. 生成されたMarkdownから「## 脚注」以降を削除
        footnote_marker = "\n## 脚注"
        footnote_index = full_markdown_text.find(footnote_marker)
        body_text = full_markdown_text[:footnote_index] if footnote_index != -1 else full_markdown_text

        # 6. [編集]リンクを正規表現で一括削除
        cleaned_body = re.sub(r'\[\[編集\]\(.+?\)]\n', '', body_text)

        # 7. タイトルと整形後の本文を結合
        final_markdown = f"# {page_title}\n\n{cleaned_body.strip()}"

        return final_markdown

    except requests.exceptions.RequestException as e:
        return f"HTTPリクエストエラー: {e}"
    except Exception as e:
        return f"予期せぬエラーが発生しました: {e}"

def get_filename_from_url(url):
    """URLからファイル名を生成する関数"""
    try:
        # URLからページ名を抽出
        parsed_url = urlparse(url)
        page_name = parsed_url.path.split('/')[-1]
        # URLデコード
        page_name = unquote(page_name)
        # ファイル名として使用できない文字を置換
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', page_name)
        return f"{safe_filename}.md"
    except:
        return "wikipedia_page.md"

def create_download_file(content, filename):
    """ダウンロード用の一時ファイルを作成する関数"""
    try:
        # 一時ディレクトリにファイルを作成
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    except Exception as e:
        print(f"ファイル作成エラー: {e}")
        return None

def create_zip_file(file_paths, zip_filename="wikipedia_export.zip"):
    """複数のファイルをZIP形式でまとめる関数"""
    try:
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # ファイル名のみを取得してZIPに追加
                    filename = os.path.basename(file_path)
                    zipf.write(file_path, filename)
        
        return zip_path
    except Exception as e:
        print(f"ZIP作成エラー: {e}")
        return None

def process_wikipedia_url(url):
    """Wikipedia URLを処理してMarkdownを生成するGradio用関数"""
    if not url:
        return "URLを入力してください。", None
    
    # URLが有効かチェック
    if not url.startswith('http'):
        return "有効なURLを入力してください（http://またはhttps://から始まるURL）。", None
    
    # Wikipedia URLかチェック
    if 'wikipedia.org' not in url:
        return "WikipediaのURLを入力してください。", None
    
    # スクレイピングを実行
    markdown_content = scrape_wikipedia_to_markdown_final(url)
    
    # ダウンロード用ファイルを作成
    if not markdown_content.startswith("エラー:") and not markdown_content.startswith("HTTP"):
        filename = get_filename_from_url(url)
        file_path = create_download_file(markdown_content, filename)
        return markdown_content, file_path
    else:
        return markdown_content, None

def process_multiple_urls(urls_text, progress=gr.Progress()):
    """複数のWikipedia URLを一括処理してMarkdownを生成する関数"""
    if not urls_text.strip():
        return "URLリストを入力してください。", None, [], None
    
    # URLリストを行ごとに分割
    urls = [url.strip() for url in urls_text.strip().split('\n') if url.strip()]
    
    if not urls:
        return "有効なURLが見つかりませんでした。", None, [], None
    
    results = []
    all_content = []
    individual_files = []
    total_urls = len(urls)
    success_count = 0
    
    for i, url in enumerate(urls):
        progress((i + 1) / total_urls, f"処理中: {i + 1}/{total_urls}")
        
        # URLの検証
        if not url.startswith('http'):
            results.append(f"❌ 無効なURL: {url}")
            continue
            
        if 'wikipedia.org' not in url:
            results.append(f"❌ Wikipedia以外のURL: {url}")
            continue
        
        # スクレイピング実行
        try:
            markdown_content = scrape_wikipedia_to_markdown_final(url)
            if markdown_content.startswith("エラー:") or markdown_content.startswith("HTTP"):
                results.append(f"❌ 処理失敗: {url}\n   エラー: {markdown_content}")
            else:
                # ページタイトルを抽出
                title_match = re.match(r'^# (.+)', markdown_content)
                page_title = title_match.group(1) if title_match else "不明なページ"
                
                # 文字数とファイル情報を表示
                char_count = len(markdown_content)
                filename = get_filename_from_url(url)
                
                results.append(f"✅ 処理成功: {url}")
                results.append(f"   📄 ページタイトル: {page_title}")
                results.append(f"   📊 文字数: {char_count:,} 文字")
                results.append(f"   💾 ファイル名: {filename}")
                
                all_content.append(markdown_content)
                success_count += 1
                
                # 個別ファイルを作成
                file_path = create_download_file(markdown_content, filename)
                if file_path:
                    individual_files.append(file_path)
        except Exception as e:
            results.append(f"❌ 処理エラー: {url}")
            results.append(f"   エラー内容: {str(e)}")
    
    # サマリー情報を追加
    summary = [
        "=" * 60,
        "📊 処理結果サマリー",
        "=" * 60,
        f"🔗 処理対象URL数: {total_urls}",
        f"✅ 成功: {success_count}",
        f"❌ 失敗: {total_urls - success_count}",
        ""
    ]
    
    # 結果を結合
    final_result = "\n".join(summary + results)
    
    # 一括ダウンロード用ファイルを作成
    batch_file_path = None
    if all_content:
        combined_content = "\n\n" + "="*80 + "\n\n".join(all_content)
        batch_file_path = create_download_file(combined_content, "wikipedia_batch_export.md")
    
    # ZIPファイルを作成
    zip_file_path = None
    if individual_files:
        zip_file_path = create_zip_file(individual_files, "wikipedia_export.zip")
    
    return final_result, batch_file_path, individual_files, zip_file_path

# Gradioインターフェースの作成
def create_interface():
    """Gradioインターフェースを作成する関数"""
    theme = create_zen_theme()
    
    with gr.Blocks(theme=theme, title="Wikipedia to Markdown Converter") as demo:
        # ヘッダー
        gr.HTML("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #d4a574 0%, #ffffff 50%, #f5f2ed 100%); color: #3d405b; border-radius: 12px;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>📚 Wikipedia to Markdown Converter</h1>
            <p style='font-size: 1.2rem; opacity: 0.8;'>WikipediaのURLを入力して、Markdown形式に変換します</p>
        </div>
        """)
        
        # タブの作成
        with gr.Tabs():
            # 単体処理タブ
            with gr.TabItem("🔗 単体処理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        url_input = gr.Textbox(
                            label="🔗 Wikipedia URL",
                            placeholder="https://ja.wikipedia.org/wiki/...",
                            value="https://ja.wikipedia.org/wiki/Python"
                        )
                        convert_btn = gr.Button("✨ 変換する", variant="primary")
                    
                    with gr.Column(scale=1):
                        output_text = gr.Textbox(
                            label="📝 変換されたMarkdown",
                            lines=20,
                            max_lines=50,
                            show_copy_button=True
                        )
                        download_file = gr.File(
                            label="📥 マークダウンファイルをダウンロード",
                            visible=False
                        )
                
                # ボタンクリック時の処理
                def update_single_output(url):
                    content, file_path = process_wikipedia_url(url)
                    if file_path:
                        return content, gr.update(value=file_path, visible=True)
                    else:
                        return content, gr.update(visible=False)
                
                convert_btn.click(
                    fn=update_single_output,
                    inputs=url_input,
                    outputs=[output_text, download_file]
                )
                
                # 使用例
                def example_process(url):
                    content, _ = process_wikipedia_url(url)
                    return content
                
                gr.Examples(
                    examples=[
                        ["https://ja.wikipedia.org/wiki/Python"],
                        ["https://ja.wikipedia.org/wiki/JavaScript"],
                        ["https://ja.wikipedia.org/wiki/HTML"]
                    ],
                    inputs=url_input,
                    outputs=output_text,
                    fn=example_process,
                    cache_examples=False
                )
            
            # 一括処理タブ
            with gr.TabItem("📋 一括処理"):
                with gr.Row():
                    with gr.Column(scale=1):
                        urls_input = gr.Textbox(
                            label="📋 Wikipedia URLリスト（1行に1つずつ）",
                            placeholder="https://ja.wikipedia.org/wiki/Python\nhttps://ja.wikipedia.org/wiki/JavaScript\nhttps://ja.wikipedia.org/wiki/HTML",
                            lines=10,
                            value="https://ja.wikipedia.org/wiki/Python\nhttps://ja.wikipedia.org/wiki/JavaScript"
                        )
                        batch_convert_btn = gr.Button("🚀 一括変換する", variant="primary")
                    
                    with gr.Column(scale=1):
                        batch_output_text = gr.Textbox(
                            label="📝 一括変換結果",
                            lines=15,
                            max_lines=30,
                            show_copy_button=True
                        )
                        batch_download_file = gr.File(
                            label="📥 全体をまとめてダウンロード",
                            visible=False
                        )
                        zip_download_file = gr.File(
                            label="🗜️ ZIPファイルでダウンロード",
                            visible=False
                        )
                        
                        # 個別ダウンロードエリア
                        individual_downloads = gr.Column(visible=False)
                        with individual_downloads:
                            gr.Markdown("### 📥 個別ダウンロード")
                            individual_file_1 = gr.File(label="", visible=False)
                            individual_file_2 = gr.File(label="", visible=False)
                            individual_file_3 = gr.File(label="", visible=False)
                            individual_file_4 = gr.File(label="", visible=False)
                            individual_file_5 = gr.File(label="", visible=False)
                
                # 一括処理ボタンクリック時の処理
                def update_batch_output(urls_text):
                    content, batch_file_path, individual_files, zip_file_path = process_multiple_urls(urls_text)
                    
                    # 戻り値のリストを準備
                    outputs = [content]
                    
                    # 一括ダウンロードファイル
                    if batch_file_path:
                        outputs.append(gr.update(value=batch_file_path, visible=True))
                    else:
                        outputs.append(gr.update(visible=False))
                    
                    # ZIPダウンロードファイル
                    if zip_file_path:
                        outputs.append(gr.update(value=zip_file_path, visible=True))
                    else:
                        outputs.append(gr.update(visible=False))
                    
                    # 個別ダウンロードエリアの表示/非表示
                    if individual_files:
                        outputs.append(gr.update(visible=True))
                    else:
                        outputs.append(gr.update(visible=False))
                    
                    # 個別ファイル（最大5つまで表示）
                    for i in range(5):
                        if i < len(individual_files):
                            filename = os.path.basename(individual_files[i])
                            outputs.append(gr.update(value=individual_files[i], visible=True, label=f"📄 {filename}"))
                        else:
                            outputs.append(gr.update(visible=False))
                    
                    return outputs
                
                batch_convert_btn.click(
                    fn=update_batch_output,
                    inputs=urls_input,
                    outputs=[
                        batch_output_text, 
                        batch_download_file,
                        zip_download_file,
                        individual_downloads,
                        individual_file_1,
                        individual_file_2,
                        individual_file_3,
                        individual_file_4,
                        individual_file_5
                    ]
                )
                
                gr.Markdown("### 💡 一括処理の使い方")
                gr.Markdown("1. テキストエリアに変換したいWikipediaのURLを1行に1つずつ入力します")
                gr.Markdown("2. 「🚀 一括変換する」ボタンをクリックします")
                gr.Markdown("3. 処理の進行状況が表示され、完了後に結果が表示されます")
                gr.Markdown("4. 各URLの処理結果（成功/失敗）が明確に表示されます")
        
        gr.Markdown("---")
        gr.Markdown("### 🎯 基本的な使用方法")
        gr.Markdown("- **単体処理**: 1つのWikipediaページを変換したい場合")
        gr.Markdown("- **一括処理**: 複数のWikipediaページを一度に変換したい場合")
        gr.Markdown("- 生成されたMarkdownは右側のテキストエリアからコピーできます")
        gr.Markdown("- **📥 ダウンロード機能**: 変換が成功すると、マークダウンファイルとして直接ダウンロードできます")
        gr.Markdown("  - 単体処理: ページ名に基づいたファイル名で個別ダウンロード")
        gr.Markdown("  - 一括処理: 各URLごとの個別ダウンロード + 全体をまとめた一括ダウンロード + **🗜️ ZIPファイル**")
        gr.Markdown("  - 個別ダウンロード: 成功した各ページを個別のファイルとしてダウンロード可能（最大5つまで表示）")
        gr.Markdown("  - **ZIPダウンロード**: 複数のMarkdownファイルを1つのZIPファイルにまとめてダウンロード")
        
        # ZENテーマの説明
        gr.HTML("""
        <div style='text-align: center; margin-top: 2rem; padding: 1.5rem; background: #ffffff; border-radius: 12px;'>
            <h3 style='color: #3d405b; margin-top: 0;'>🧘‍♀️ ZENテーマ</h3>
            <p style='color: #8b7355;'>和モダンなデザインで、使いやすさと美しさを追求しました</p>
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
