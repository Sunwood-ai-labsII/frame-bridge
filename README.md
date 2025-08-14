---
license: mit
title: frame bridge
sdk: gradio
emoji: 🏆
colorFrom: red
colorTo: indigo
thumbnail: >-
  https://cdn-uploads.huggingface.co/production/uploads/64e0ef4a4c78e1eba5178d7a/BZfofcX1vEF7kwWQ0i-uB.png
sdk_version: 5.42.0
---

<div align="center">

![frame-bridge](https://github.com/user-attachments/assets/05977e5b-3e63-4ed2-a5f6-74ada8943994)

# 📚 Wikipedia to Markdown Converter

*WikipediaページをMarkdown形式に変換するWebアプリケーション*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-5.42+-FF6B6B?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Demo](https://img.shields.io/badge/🚀%20デモサイト-Live-orange?style=for-the-badge)](https://huggingface.co/spaces/MakiAi/wikipedia-to-markdown)

</div>

---

## 🌟 概要

**Wikipedia to Markdown Converter** は、Wikipediaの記事を整形されたMarkdownドキュメントに変換するWebアプリケーションです。単体処理と一括処理に対応し、複数のダウンロード形式を提供します。

### ✨ **主要機能**

- 🔄 **単体・一括処理** - 1つまたは複数のWikipediaページを同時変換
- 📊 **詳細分析** - 文字数、成功率、ファイル情報を表示
- 🗜️ **複数形式** - 個別ファイル、結合文書、ZIPダウンロード
- 🌐 **多言語対応** - 全てのWikipedia言語版に対応
- � **要使いやすいUI** - 直感的で美しいインターフェース

---

## 🚀 使い方

### �  **オンラインで試す（推奨）**
**[🚀 デモサイトはこちら](https://huggingface.co/spaces/MakiAi/wikipedia-to-markdown)**

### 💻 **ローカルで実行**

```bash
# リポジトリをクローン
git clone https://github.com/your-username/wikipedia-to-markdown.git
cd wikipedia-to-markdown

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python app.py
```

### 🐳 **Dockerで実行**

```bash
# Docker Composeを使用
docker-compose up -d

# ブラウザで http://localhost:7860 にアクセス
```

---

## 📋 操作方法

### 🔗 **単体処理**
1. WikipediaのURLを入力
2. 「✨ 変換する」ボタンをクリック
3. 生成されたMarkdownをコピーまたはダウンロード

### 📚 **一括処理**
1. 複数のURLを1行に1つずつ入力
2. 「🚀 一括変換する」ボタンをクリック
3. 処理結果を確認し、必要な形式でダウンロード

### 📊 **処理結果の表示例**
```
============================================================
📊 処理結果サマリー
============================================================
🔗 処理対象URL数: 3
✅ 成功: 2
❌ 失敗: 1

✅ 処理成功: https://ja.wikipedia.org/wiki/Python
   📄 ページタイトル: Python
   📊 文字数: 15,432 文字
   💾 ファイル名: Python.md
```

---

## 📦 ダウンロード形式

| 形式 | 説明 | 用途 |
|------|------|------|
| **📄 個別ファイル** | 各ページを別々のMarkdownファイル | 個別編集・管理 |
| **📚 結合文書** | 全ページを1つのファイルに結合 | 一括閲覧・印刷 |
| **🗜️ ZIPアーカイブ** | 全ファイルを圧縮してまとめて | 大量ファイルの管理 |

---

## 🔧 技術仕様

### **使用技術**
- **Python 3.8+** - メイン言語
- **Gradio** - Webインターフェース
- **BeautifulSoup4** - HTML解析
- **html2text** - Markdown変換
- **Requests** - HTTP通信

### **処理フロー**
1. **URL検証** - 入力URLの妥当性チェック
2. **HTML取得** - Wikipediaページの取得
3. **コンテンツ抽出** - 主要コンテンツの抽出
4. **クリーンアップ** - 不要部分（脚注、編集リンク等）の削除
5. **Markdown変換** - 整形されたMarkdownに変換
6. **ファイル生成** - 各種形式でのファイル出力

---

## 📁 プロジェクト構成

```
wikipedia-to-markdown/
├── app.py                    # メインアプリケーション
├── theme.py                  # UIテーマ設定
├── requirements.txt          # Python依存関係
├── docker-compose.yml        # Docker設定
├── .github/workflows/        # CI/CD設定
└── README.md                 # このファイル
```

---

## 🛠️ カスタマイズ

### **テーマ変更**
`theme.py`を編集してUIの色やスタイルを変更できます。

### **処理ロジック拡張**
`app.py`の`scrape_wikipedia_to_markdown_final()`関数を編集して、変換処理をカスタマイズできます。

---

## 📄 ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

---

## 🤝 コントリビューション

バグ報告や機能提案は[GitHub Issues](https://github.com/your-username/wikipedia-to-markdown/issues)でお願いします。

---

<div align="center">

**🌟 このプロジェクトが役に立ったらスターをお願いします！**

*© 2025 Wikipedia to Markdown Converter*

</div>
