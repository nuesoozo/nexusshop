import os
import asyncio
import threading
from flask import Flask
from bot import main as run_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
    # Исправление для Python 3.10+ (чтобы не было ошибки event loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run_bot()

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    threading.Thread(target=start_bot, daemon=True).start()
    
    # Запускаем Flask для Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
