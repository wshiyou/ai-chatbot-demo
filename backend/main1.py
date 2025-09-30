# backend/main1.py
import os
from pathlib import Path
from typing import Optional
from uuid import uuid4
from collections import defaultdict
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Body, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from openai import AzureOpenAI

# =========================================
# .env 読み込み（Azure OpenAI の設定値を取得）
# =========================================
load_dotenv()
AZ_ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT")
AZ_API_KEY     = os.getenv("AZURE_OPENAI_API_KEY")
AZ_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT")  
AZ_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

if not (AZ_ENDPOINT and AZ_API_KEY and AZ_DEPLOYMENT):
    raise RuntimeError("Azure OpenAI の環境変数が不足しています（backend/.env を確認）。")

client = AzureOpenAI(
    api_key=AZ_API_KEY,
    api_version=AZ_API_VERSION,
    azure_endpoint=AZ_ENDPOINT,
)

# ==========================
# FastAPI アプリ基礎設定
# ==========================
app = FastAPI(title="Chatbot Backend (Azure Proxy)")

# 開発中は緩めでOK（本番は必要最小限に絞ってください）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
# /static/ に frontend ディレクトリを丸ごとマウント
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def index():
    """トップページ：/frontend/index.html を返す"""
    return FileResponse(str(FRONTEND_DIR / "index.html"))

# ====================================
# 会話メモリ（インメモリ：再起動で消える）
# キー: sid(cookie) → 値: messages(list)
# ====================================
SESSIONS = defaultdict(list)

# ==========================
# リクエスト/レスポンス定義
# ==========================
class ChatRequest(BaseModel):
    # フロントからは message のみ送ればOK（sidはCookieで管理）
    message: str = Field(..., min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    reply: str
    sessionId: str  # 実際に利用した sid（Cookieと同じ値を返す）

# ==================================================
# 履歴トリミング：トークン節約のため最近の発話だけ残す
# ==================================================
MAX_TURNS = 20  # system を除く直近メッセージ数（user/assistant 合計）

def trim_history(history: list[dict]) -> list[dict]:
    """最初の system を 1 件保持 + 直近の発話だけ残して返す"""
    system = [m for m in history if m.get("role") == "system"][:1]
    rest   = [m for m in history if m.get("role") != "system"][-MAX_TURNS:]
    return system + rest

# ==========================
# チャット API（Cookie で sid を固定）
# ==========================
@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    # 1) Cookie から sid 取得。無ければ新規発行
    sid: Optional[str] = request.cookies.get("sid")
    if not sid:
        sid = str(uuid4())

    # 2) message バリデーション
    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message is empty")

    try:
        # 3) 履歴取得＆今回の user を追加
        history = SESSIONS[sid]
        if not history:
            history.append({"role": "system", "content": "あなたは丁寧で親切なアシスタントです。"})
        history.append({"role": "user", "content": msg})

        # デバッグ：送信前の履歴長
        print(f"[chat] sid={sid} before={len(history)}", flush=True)

        # 4) Azure OpenAI 呼び出し（履歴込み）
        resp = client.chat.completions.create(
            model=AZ_DEPLOYMENT,               # Azureの「デプロイ名」
            messages=trim_history(history),
            temperature=0.7,
            timeout=60,
        )
        reply = (resp.choices[0].message.content or "").strip()

        # 5) assistant 追加＆保存
        history.append({"role": "assistant", "content": reply})
        SESSIONS[sid] = history

        # デバッグ：送信後の履歴長
        print(f"[chat] sid={sid} after={len(history)}", flush=True)

        # 6) Cookie を設定して返す（7日保持・必要に応じて調整）
        r = JSONResponse({"reply": reply, "sessionId": sid})
        r.set_cookie(
            key="sid",
            value=sid,
            max_age=7 * 24 * 3600,   # 7 days
            httponly=True,
            samesite="lax",
        )
        return r

    except Exception as e:
        import traceback
        print("=== Azure OpenAI Error ===")
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Azure OpenAI error: {type(e).__name__}: {e}")

# ==========================
# セッション履歴のリセット（任意）
# ==========================
@app.post("/api/reset")
async def reset(sessionId: str = Body(..., embed=True)):
    """指定セッションの履歴を削除（新しい会話として開始）"""
    SESSIONS.pop(sessionId, None)
    return {"ok": True}

# ==========================
# デバッグ：現在のセッション一覧
# ==========================
@app.get("/api/debug/sessions")
async def debug_sessions():
    return [
        {"sessionId": sid, "len": len(hist)}
        for sid, hist in SESSIONS.items()
    ]

# ==========================
# デバッグ：個別セッションの履歴（末尾のみ）
# ==========================
@app.get("/api/debug/history")
async def debug_history(sessionId: str = Query(...)):
    hist = SESSIONS.get(sessionId, [])
    return {"len": len(hist), "last_messages": hist[-8:]}
