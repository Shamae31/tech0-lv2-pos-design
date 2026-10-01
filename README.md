# 簡易POSアプリ改（Lv2）

要件定義書に基づく Next.js / FastAPI / MySQL 構成です。秘密情報は `.env` にのみ保存してください。

## 起動

```bash
cp .env.example .env
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --env-file ../.env --reload --port 8000
```

別ターミナルで:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

共有MySQLの**サーバー名**と、このアプリ専用の**データベース名**は別です。専用データベースを作成してから `backend/sql/schema.sql` を適用し、レジ担当者・商品・税率などのマスタを登録してください。既存の他人のデータベースに適用しないでください。

担当者パスワードのハッシュ生成:

```bash
backend/.venv/bin/python backend/scripts/hash_password.py
```

購入確定時はBackendが商品価格・会員・販促ルール・税率をDBから再取得し、取引と明細を1トランザクションで保存します。
既存DBでは、デプロイ前に `backend/sql/migrate_idempotency.sql` を一度だけ適用してください。新規DBでは `backend/sql/schema.sql` に含まれます。商品価格変更は `backend/sql/change_product_price.example.sql` を参考に現在価格と履歴を同一トランザクションで更新してください。

## 構成

- `backend/app/api/`: 機能別のAPIエンドポイント
- `backend/app/core/`: DB接続・認証・環境設定
- `backend/app/services/`: 税・金額計算などの業務ルール
- `backend/app/schemas.py`: API入力モデル
- `frontend/app/components/`: 会員確認・商品登録・購入リスト・履歴などの画面部品
- `frontend/app/lib/`: API通信・型・表示用金額計算

購入前の金額はBackendがマスタと割引ルールから計算します。購入確定時に同じ条件で再計算し、表示金額と異なる場合は保存せず再確認を求めます。購入要求IDで再送時の二重登録を防ぎます。確定済み取引はFR-15に従って閲覧専用です。

商品画像は画像本体ではなく `products.image_url` にAzure Blob Storage等のHTTPS URLを保存します。画像が未登録の場合は商品名の先頭文字を表示します。

## Azure App Service への公開

Next.jsとFastAPIを別々のLinux App Serviceに配置します。MySQL Flexible Serverには `backend/sql/schema.sql`（既存DBなら先に `migrate_idempotency.sql`）を適用します。投入する担当者のパスワードは `backend/scripts/hash_password.py` でハッシュ化します。

- API App Service: Python、起動コマンド `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`。アプリ設定に `POS_ENV=production`、`POS_DEMO_MODE=0`、`JWT_SECRET`（32文字以上のランダム値）、`MYSQL_HOST`、`MYSQL_DATABASE`、`MYSQL_USER`、`MYSQL_PASSWORD`、必要なら `MYSQL_SSL_CA`、`CORS_ORIGINS=https://<frontend-host>` を設定。接続先証明書とホスト名を検証します。
- Frontend App Service: Node.js、`frontend` ディレクトリで `npm ci` と `npm run build` を実行し、`npm run start` で起動。アプリ設定に `API_BASE_URL=https://<api-host>` を指定します。ブラウザは同一オリジンの `/api` を呼び、Next.jsのサーバー側がAPIに中継します。内部APIのURLをブラウザへ公開する必要はありません。
- APIの `https://<api-host>/health` とFrontendの公開URLを確認し、ログイン・購入前金額・購入確定・取引履歴を実DBで確認してください。HTTPのURLやローカルホストを公開用設定に残さないでください。APIがAzure内限定の場合は、Frontendから接続できる同じネットワークに配置してください。

公開URLはAzureへの配置と疎通確認後に案内します。既存の別アプリは上書きしません。

テスト:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```
