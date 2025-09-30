AI Chatbot Web App

A simple chatbot built with FastAPI and Azure OpenAI.
Supports conversation memory, dark mode, and clear history.

シンプルなチャットボット（FastAPI + Azure OpenAI 使用）。
会話履歴の記憶、ダークモード切替、履歴クリア機能をサポート。

Features / 機能

Session-based conversation memory / セッション単位の会話記憶

Dark mode toggle / ダークモード切替

Clear chat history button / 履歴クリアボタン

Frontend: HTML/CSS/JavaScript

Backend: FastAPI

Getting Started / セットアップ
git clone https://github.com/your-username/ai-chatbot-demo.git
cd ai-chatbot-demo
pip install -r requirements.txt


Create backend/.env file / .env ファイルを作成:

AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2025-01-01-preview


Run the app / アプリを起動:

uvicorn backend.main:app --reload


Open / ブラウザでアクセス 👉 http://localhost:8000

License / ライセンス

MIT