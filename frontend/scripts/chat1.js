// frontend/scripts/chat.js
const API_BASE = "/api/chat";

let chatEl, inputEl, sendBtn;
let sending = false;

document.addEventListener("DOMContentLoaded", () => {
  console.log("[chat.js] loaded");

  chatEl  = document.getElementById("chat");
  inputEl = document.getElementById("input");
  sendBtn = document.getElementById("send");

  if (sendBtn) {
    sendBtn.onclick = null;
    sendBtn.addEventListener("click", send);
  }
  if (inputEl) {
    inputEl.addEventListener("keydown", (e) => {
      const composing = e.isComposing || e.key === "Process" || e.keyCode === 229;
      if (composing) return;
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });
  }

  if (chatEl) addMessage("bot", "こんにちは！ここにメッセージを入力して送信してください。");

  // テーマボタン
  const themeBtn = document.createElement("button");
  themeBtn.textContent = "🌓 テーマ切替";
  Object.assign(themeBtn.style, {
    position: "fixed", top: "10px", right: "10px",
    padding: "6px 10px", borderRadius: "6px",
    border: "1px solid transparent", background: "#333", color: "#fff",
    cursor: "pointer", zIndex: "9999"
  });
  document.body.appendChild(themeBtn);
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("chat_theme", document.body.classList.contains("dark") ? "dark" : "light");
  });
  const saved = localStorage.getItem("chat_theme");
  if (saved === "dark") document.body.classList.add("dark");
});

function addMessage(role, content) {
  if (!chatEl) return;
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  const avatar = document.createElement("img");
  avatar.className = "avatar";
  if (role === "bot") { avatar.src = "/static/images/robot.png"; avatar.alt = "bot"; }
  else { avatar.src = "/static/images/user.png"; avatar.alt = "user"; }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  if (role === "bot") { div.appendChild(avatar); div.appendChild(bubble); }
  else { div.appendChild(bubble); div.appendChild(avatar); }
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function send() {
  if (sending || !inputEl) return;
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = "";
  addMessage("user", text);

  const thinking = document.createElement("div");
  thinking.className = "msg bot";
  thinking.textContent = "考え中…";
  chatEl.appendChild(thinking);
  chatEl.scrollTop = chatEl.scrollHeight;

  sending = true;
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // ★ Cookie で sid を管理するので message のみ送る
      body: JSON.stringify({ message: text })
    });

    // 失敗時も詳細を見たいので一旦テキストで受ける
    const bodyText = await res.text();
    let data = null;
    try { data = JSON.parse(bodyText); } catch {}

    if (!res.ok) {
      thinking.remove();
      console.error("[chat error]", res.status, res.statusText, bodyText);
      addMessage("bot", `HTTP ${res.status} ${res.statusText}\n${bodyText}`);
      return;
    }

    thinking.remove();
    // 右下に sid バッジを表示（クリックで /api/debug/history を開く）
    if (data && data.sessionId) {
      let badge = document.getElementById("sid-badge");
      if (!badge) {
        badge = document.createElement("div");
        badge.id = "sid-badge";
        Object.assign(badge.style, {
          position: "fixed", right: "10px", bottom: "10px",
          background: "#222", color: "#0f0", padding: "6px 8px",
          borderRadius: "6px", font: "12px/1.4 monospace", zIndex: 9999,
          cursor: "pointer"
        });
        badge.title = "クリックで /api/debug/history を開く";
        badge.addEventListener("click", () => {
          window.open(`/api/debug/history?sessionId=${encodeURIComponent(data.sessionId)}`, "_blank");
        });
        document.body.appendChild(badge);
      }
      badge.textContent = `sid: ${data.sessionId}`;
    }

    addMessage("bot", (data && data.reply) || "(no reply)");
  } catch (e) {
    thinking.remove();
    addMessage("bot", "エラー: " + (e?.message || e));
  } finally {
    sending = false;
    if (sendBtn) sendBtn.disabled = false;
  }
}
