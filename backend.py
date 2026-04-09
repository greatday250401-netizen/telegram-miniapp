"""
backend.py
─────────────────────────────────────────────────────────────
Simple Flask backend that:
  1. Receives queries from the Mini App
  2. Forwards them to a Telegram bot
  3. Polls for the bot's response
  4. Returns it to the Mini App

Deploy this to: Heroku, Railway, Render, or Replit (all have free tiers)
─────────────────────────────────────────────────────────────
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os

app = Flask(__name__)
CORS(app)

# ── Config ─────────────────────────────────────────────────────────────────
BOT_TOKEN = "8590813298:AAGj7s6jSpTj12-1BWiVaFLc527wy9e_nGI"
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
POLL_TIMEOUT = 10  # seconds to wait for response
POLL_INTERVAL = 0.5  # check every 500ms
# ───────────────────────────────────────────────────────────────────────────

# Track last_update_id per user to avoid reading old messages
last_update_ids = {}


@app.route("/query", methods=["POST"])
def handle_query():
    """
    Receives: { "query": "...", "user_id": 123456789 }
    Returns: { "status": "success", "response": "bot's answer", "error": null }
    """
    try:
        data = request.json
        query = data.get("query")
        user_id = data.get("user_id")

        if not query or not user_id:
            return jsonify({"status": "error", "response": None, "error": "Missing query or user_id"}), 400

        # Step 1: Send message to bot
        send_result = requests.post(
            f"{BOT_API_URL}/sendMessage",
            json={"chat_id": user_id, "text": query},
            timeout=5
        )
        if not send_result.ok:
            return jsonify({"status": "error", "response": None, "error": "Failed to send message to bot"}), 500

        # Step 2: Poll for response
        response_text = poll_for_response(user_id)

        if response_text:
            return jsonify({
                "status": "success",
                "response": response_text,
                "error": None
            })
        else:
            return jsonify({
                "status": "timeout",
                "response": None,
                "error": "No response from bot within timeout period"
            }), 408

    except Exception as e:
        return jsonify({"status": "error", "response": None, "error": str(e)}), 500


def poll_for_response(user_id, timeout=POLL_TIMEOUT):
    """
    Poll getUpdates to find the bot's response message from this user.
    Returns the message text if found, None if timeout.
    """
    start_time = time.time()
    last_update_id = last_update_ids.get(user_id, 0)

    while time.time() - start_time < timeout:
        try:
            result = requests.post(
                f"{BOT_API_URL}/getUpdates",
                json={"offset": last_update_id + 1, "timeout": 0},
                timeout=5
            )
            result.raise_for_status()
            updates = result.json().get("result", [])

            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message", {})
                msg_user_id = message.get("from", {}).get("id")
                text = message.get("text")

                # Store latest update_id to avoid re-reading old messages
                if update_id > last_update_id:
                    last_update_id = update_id

                # Found a response from this user
                if msg_user_id == user_id and text:
                    last_update_ids[user_id] = last_update_id
                    return text

            # No message yet, wait a bit
            time.sleep(POLL_INTERVAL)

        except requests.RequestException:
            time.sleep(POLL_INTERVAL)

    # Timeout reached
    return None


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # For development: python backend.py
    # For production: gunicorn backend:app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
