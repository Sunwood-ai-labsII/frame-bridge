---
license: mit
title: frame bridge
sdk: gradio
emoji: 🎬
colorFrom: purple
colorTo: blue
thumbnail: >-
  https://cdn-uploads.huggingface.co/production/uploads/64e0ef4a4c78e1eba5178d7a/BZfofcX1vEF7kwWQ0i-uB.png
sdk_version: 5.42.0
---

<div align="center">

![frame-bridge](https://github.com/user-attachments/assets/05977e5b-3e63-4ed2-a5f6-74ada8943994)

# 🎬 Frame Bridge

*2つの動画を最適なフレームで自動結合するAIアプリケーション*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![Gradio](https://img.shields.io/badge/Gradio-5.42+-FF6B6B?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Demo](https://img.shields.io/badge/🚀%20デモサイト-Live-orange?style=for-the-badge)](https://huggingface.co/spaces/MakiAi/frame-bridge)

</div>

---

## 🌟 概要

**Frame Bridge** は、複数の動画を視覚的に最適なフレームで自動結合するAIバッチ処理アプリケーションです。SSIM（構造的類似性指標）を使用して、動画間の最も類似したフレームを検出し、スムーズな動画結合を実現します。

### ✨ **主要機能**

- 🤖 **AI自動分析** - SSIM技術による高精度フレーム類似度計算
- 🎯 **最適接続点検出** - 動画間の最も自然な結合点を自動検出
- 📁 **バッチ処理** - 複数動画の一括処理とレポート生成
- 📤 **ファイルアップロード** - ローカルファイルを直接アップロードして処理
- 🎬 **スムーズ結合** - 視覚的に自然な動画結合を実現
- 📊 **詳細レポート** - 処理結果の詳細分析とレポート出力

---

## 🚀 使い方

### 🌐 **オンラインで試す（推奨）**
**[🚀 デモサイトはこちら](https://huggingface.co/spaces/MakiAi/frame-bridge)**

### 💻 **ローカルで実行**

```bash
# リポジトリをクローン
git clone https://github.com/Sunwood-ai-labsII/frame-bridge.git
cd frame-bridge

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

### 🎬 **バッチ動画結合の手順**
1. **動画ファイルアップロード** - 結合したい複数の動画ファイルを選択してアップロード
2. **処理モード選択** - 順次結合またはペア結合を選択
3. **出力ファイル名設定** - 順次結合の場合の最終ファイル名を指定
4. **バッチ処理実行** - AIが最適な接続点を自動検出して一括結合

### 📊 **処理モード**
- **順次結合**: アップロードした全動画を名前順に1つの動画に結合
- **ペア結合**: 動画を2つずつペアにして結合（複数の出力ファイル）

### 📊 **分析結果の表示例**
```
🎬 バッチ処理完了！

📊 処理結果:
✅ 順次結合完了!
📁 出力ファイル: merged_sequence.mp4

📋 詳細レポート:
• 総処理数: 3
• 成功: 3
• 失敗: 0
• 平均類似度: 0.847
```

---

## 🎯 技術的特徴

| 技術 | 説明 | 効果 |
|------|------|------|
| **SSIM分析** | 構造的類似性指標による高精度フレーム比較 | 視覚的に自然な結合点検出 |
| **自動最適化** | AI による最適接続フレーム自動検出 | 手動編集不要 |
| **リアルタイム分析** | 動画アップロード時の即座情報表示 | 効率的なワークフロー |

---

## 🔧 技術仕様

### **使用技術**
- **Python 3.8+** - メイン言語
- **OpenCV** - 動画処理・フレーム抽出
- **scikit-image** - SSIM計算
- **Gradio** - Webインターフェース
- **NumPy** - 数値計算
- **Pillow** - 画像処理
- **html2text** - Markdown変換
- **Requests** - HTTP通信

### **処理フロー**
1. **動画アップロード** - 2つの動画ファイルをアップロード
2. **フレーム抽出** - 各動画から代表フレームを抽出
3. **類似度計算** - SSIM技術による高精度フレーム比較
4. **最適点検出** - 最も類似度の高い接続フレームを特定
5. **動画結合** - 検出された最適点で動画を結合
6. **結果出力** - 結合動画と分析結果を提供

---

## 📁 プロジェクト構成

```
frame-bridge/
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

### **アルゴリズム調整**
`app.py`の`find_best_connection_frames()`関数を編集して、フレーム分析ロジックをカスタマイズできます。

### **類似度閾値調整**
SSIM計算の精度や比較フレーム数を調整して、結合品質を最適化できます。

---

## 📄 ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。

---

## 🤝 コントリビューション

バグ報告や機能提案は[GitHub Issues](https://github.com/Sunwood-ai-labsII/frame-bridge/issues)でお願いします。

---

<div align="center">

**🌟 このプロジェクトが役に立ったらスターをお願いします！**

*© 2025 Frame Bridge - AI Video Merger*

</div>
