import os
import json
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, PreCheckoutQueryHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_RAW = os.getenv("ADMIN_ID")
ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW else None
WEBAPP_URL = "https://nuesoozo.github.io/nexusshop/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("Поддержка", callback_data="support")]
    ]
    await update.message.reply_text(
        "Добро пожаловать в NEXUS SHOP!\n\n"
        "Здесь вы можете приобрести игровую валюту, а также читы на Автообмен и Казино для Black Russia.\n\n"
        "Надежность, качество и быстрая выдача — наш главный приоритет.\n\n"
        "Выберите интересующий вас раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Напишите свой вопрос или проблему. Мы ответим в скором времени.")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    
    if data.get('type') == 'virts':
        title = f"Покупка виртов ({data['amount']} млн)"
        desc = f"Ник: {data['nick']}"
        price = int(data['price'])
    elif data.get('type') == 'cheat':
        title = f"Чит: {data['name']}"
        desc = "Цифровой товар"
        price = int(data['price'])
    else:
        return

    # Создаём ссылку на оплату
    invoice_link = await context.bot.create_invoice_link(
        title=title,
        description=desc,
        payload=json.dumps(data),
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=price)]
    )
    
    # Возвращаем ссылку на сайт
    await context.bot.answer_web_app_query(
        web_app_query_id=update.effective_message.web_app_data.query_id,
        result={
            "type": "article",
            "id": "1",
            "title": "Оплата",
            "input_message_content": {
                "message_text": invoice_link
            }
        }
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    data = json.loads(payment.invoice_payload)
    
    await update.message.reply_text("Оплата прошла успешно! Заказ передан в обработку.")
    
    if ADMIN_ID:
        username = update.effective_user.username or update.effective_user.id
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"НОВАЯ ПОКУПКА!\n\nДанные: {json.dumps(data, ensure_ascii=False)}\nПокупатель: @{username}"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
