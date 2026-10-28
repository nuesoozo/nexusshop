import os
import threading
from flask import Flask
from bot import main as run_bot  # Импортируем запуск твоего бота

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
    run_bot()

if __name__ == "__main__":
    # Запускаем бота в фоне
    threading.Thread(target=start_bot, daemon=True).start()
    
    # Запускаем Flask, чтобы Render видел порт
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
