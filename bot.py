import os
import json
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, PreCheckoutQueryHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBAPP_URL = os.getenv("WEBAPP_URL") # Ссылка на твой GitHub Pages

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

# Ловим данные с сайта (Mini App)
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    
    if data['type'] == 'virts':
        title = f"Покупка виртов ({data['amount']} млн)"
        desc = f"Ник: {data['nick']}"
        price = data['price']
    elif data['type'] == 'cheat':
        title = f"Чит: {data['name']}"
        desc = "Цифровой товар"
        price = data['price']

    # Отправляем счет на оплату в Stars
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=title,
        description=desc,
        payload=json.dumps(data), # Сохраняем данные в чеке
        provider_token="", 
        currency="XTR", # XTR = Telegram Stars
        prices=[LabeledPrice(label=title, amount=price)]
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    data = json.loads(payment.invoice_payload)
    
    await update.message.reply_text("Оплата прошла успешно! Заказ передан в обработку.")
    
    # Уведомление тебе в личку
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
    app.run_polling()

if __name__ == "__main__":
    main()
