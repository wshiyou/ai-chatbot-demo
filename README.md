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


## Screenshots / スクリーンショット
### 1. Initial Screen / 起動画面

<img width="1103" height="1033" alt="スクリーンショット 2025-09-30 14 57 04" src="https://github.com/user-attachments/assets/ed658766-e10d-42f0-846a-e70960059352" />
When you open the app, you see a clean chat interface where you can immediately start interacting with the bot.  
アプリを起動すると、シンプルなチャット画面が表示され、すぐにボットとの会話を開始できます。

### 2. Chatting Example / チャット例

<img width="1196" height="977" alt="スクリーンショット 2025-09-30 15 12 38" src="https://github.com/user-attachments/assets/ef6542cc-72f3-4559-aa8a-40ab459edf89" />

The user can type a message and the bot responds with context.  
ユーザーがメッセージを入力すると、ボットが文脈に基づいて応答します。

### 3. Dark Mode / ダークモード

<img width="1055" height="1007" alt="スクリーンショット 2025-09-30 15 13 29" src="https://github.com/user-attachments/assets/7dd388d4-e303-4a5e-8dee-545e8abfd3dc" />

Users can toggle between light and dark themes for better usability.  
ユーザーはライトモードとダークモードを切り替えて、使いやすさを向上させることができます。













