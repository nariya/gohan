# GohanMap

Google Mapsを使った店舗検索ツール。好みや検索履歴をデータベースに保存できます。

## 技術スタック

- **バックエンド**: Python + FastAPI + SQLAlchemy
- **フロントエンド**: Next.js + React + TypeScript + Tailwind CSS
- **データベース**: SQLite
- **API**: Google Maps Places API

## セットアップ

### バックエンド

1. 依存関係をインストール:
```bash
cd backend
pip install -r requirements.txt
```

2. Playwrightのセットアップ:
```bash
python setup_playwright.py
# または手動で: python -m playwright install chromium
```

3. 環境変数を設定:
```bash
cp .env.example .env
# .envファイルにGoogle Maps APIキーとOpenAI APIキーを設定
```

4. サーバーを起動:
```bash
uvicorn main:app --reload
```

### フロントエンド

1. 依存関係をインストール:
```bash
cd frontend
npm install
```

2. 環境変数を設定:
```bash
cp .env.local.example .env.local
# .env.localファイルにGoogle Maps APIキーを設定
```

3. 開発サーバーを起動:
```bash
npm run dev
```

## 機能

### 通常検索
- **店舗検索**: Google Maps Places APIを使用した店舗検索
- **地図表示**: インタラクティブな地図上にお店を表示
- **お気に入り機能**: 気に入ったお店をデータベースに保存
- **検索履歴**: 過去の検索クエリを自動保存

### AI検索 ✨
- **自然言語処理**: 「女性に受けるラーメン屋さん」などの自然な検索
- **クエリ解析**: DeepSeek AIを使った検索意図の理解（コスパ重視）
- **複合検索**: API + スクレイピング の組み合わせ検索
- **AIランキング**: 検索条件に基づく店舗の自動評価・ランキング
- **検索サマリー**: AI生成の検索結果要約

### 詳細検索（スクレイピング）
- **Playwright自動化**: ブラウザ自動化によるGoogle Mapsスクレイピング
- **詳細情報取得**: 店名、住所、評価、電話番号、営業時間、カテゴリなど
- **データベース保存**: スクレイピング結果の自動保存と管理
- **重複防止**: 既存データとの重複チェック機能

### 共通機能
- **レスポンシブデザイン**: モバイル対応UI
- **3タブ切り替え**: 通常検索・AI検索・詳細検索の切り替え

## API エンドポイント

### 通常検索
- `GET /api/search/places` - Google Maps Places API経由の店舗検索
- `POST /api/favorites` - お気に入り追加
- `GET /api/favorites/{user_id}` - ユーザーのお気に入り一覧
- `GET /api/history` - 検索履歴一覧

### AI検索
- `GET /api/ai/search` - 自然言語によるAI検索（複合検索 + AIランキング）

### スクレイピング
- `GET /api/scrape/places` - Playwrightによる詳細検索
- `GET /api/scraped/places` - スクレイピング済みデータ一覧

## API設定

### Google Maps API
1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Maps JavaScript API と Places API を有効化
3. APIキーを作成し、適切な制限を設定
4. `.env`と`.env.local`にAPIキーを設定

### DeepSeek API
1. [DeepSeek Platform](https://platform.deepseek.com/)でアカウント作成
2. APIキーを生成（コスパ最高！）
3. `.env`と`.env.local`にAPIキーを設定

## 使用例

### AI検索の例
- 「女性に受けるラーメン屋さん」
- 「デートで使える高級フレンチ」
- 「家族連れにおすすめのイタリアン」
- 「一人でも入りやすいおしゃれなカフェ」
- 「コスパの良い焼肉店」