import threading
import asyncio
from dotenv import load_dotenv
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from main import get_token_data
from models import init_db, save_response, get_all_alerts, delete_alert

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, welcome to the trading assistant robot. Use /active to see options.')

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['Current cryptocurrency price'],
        ['Create a price alert']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Please select an option:', reply_markup=reply_markup)

async def current_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Current price of Bitcoin", callback_data='Current_Bitcoin')],
        [InlineKeyboardButton("Current price of Ethereum", callback_data='Current_Ethereum')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select the desired cryptocurrency', reply_markup=reply_markup)

async def Current_Bitcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_bitcoin = update.callback_query
    await query_bitcoin.answer()
    result_bitcoin = get_token_data('bitcoin')
    await query_bitcoin.edit_message_text(f"Current price of Bitcoin: {result_bitcoin}")

async def Current_Ethereum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_ethereum = update.callback_query
    await query_ethereum.answer()
    result_ethereum = get_token_data('ethereum')
    await query_ethereum.edit_message_text(f"Current price of Ethereum: {result_ethereum}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'Current_Bitcoin':
        await Current_Bitcoin(update, context)
    elif query.data == 'Current_Ethereum':
        await Current_Ethereum(update, context)

cryptocurrencies = ["bitcoin", "ethereum"]
user_data = {}

async def price_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data.clear()
    await show_crypto_options(update)

async def show_crypto_options(update: Update):
    keyboard = [[InlineKeyboardButton(crypto.capitalize(), callback_data=crypto) for crypto in cryptocurrencies]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select the desired cryptocurrency:', reply_markup=reply_markup)

async def handle_crypto_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data["cryptocurrency"] = query.data
    price = get_token_data(query.data)
    await query.edit_message_text(
        f"You have selected {query.data.capitalize()} with the current price of {price}. "
        "At what price should I alert you? Please send the price."
    )

async def handle_warning_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        warning_price = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Please send a valid price.")
        return

    user_data["warning_price"] = warning_price

    current_price_str = get_token_data(user_data["cryptocurrency"])

    try:
        current_price = float(current_price_str.replace('$', '').replace(',', '').strip())
    except ValueError:
        await update.message.reply_text("Could not retrieve the current price. Please try again later.")
        return

    if warning_price > current_price:
        user_data["price_condition"] = "More than"
    else:
        user_data["price_condition"] = "Less than"

    chat_id = update.message.chat.id
    save_response(chat_id,
                  user_data.get("cryptocurrency"),
                  user_data.get("warning_price"),
                  user_data["price_condition"])

    await update.message.reply_text(
        f"If the price of {user_data['cryptocurrency'].capitalize()} is {'higher' if user_data['price_condition'] == 'More than' else 'lower'} than {user_data['warning_price']}, we will inform you."
    )

app = ApplicationBuilder().token(TOKEN).build()

init_db()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Current cryptocurrency price"), current_price))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Create a price alert"), price_alert))
app.add_handler(CommandHandler("active", active))
app.add_handler(CallbackQueryHandler(button_click, pattern='Current_Bitcoin|Current_Ethereum'))  # هندلر برای انتخاب ارز
app.add_handler(CallbackQueryHandler(handle_crypto_choice, pattern='|'.join(cryptocurrencies)))  # هندلر برای انتخاب ارز دیجیتال
app.add_handler(MessageHandler(filters.TEXT, handle_warning_price))  # هندلر برای دریافت قیمت هشدار

async def send_reminders():
    bot = Bot(token=TOKEN)
    while True:
        print('to check:')
        alerts = get_all_alerts()
        for alert in alerts:
            alert_id = alert['id']
            chat_id = alert['chat_id']
            cryptocurrency = alert['cryptocurrency']
            warning_price = alert['warning_price']
            price_condition = alert['price_condition']
            current_price_str = get_token_data(cryptocurrency)
            current_price = float(current_price_str.replace('$', '').replace(',', '').strip())
            if 'More than' == price_condition:
                print(f'Current price:{current_price} Warning price:{int(warning_price)}')
                if int(warning_price) <= current_price:
                    message = (
                    f"Alert! The price of {cryptocurrency.capitalize()} is now "
                    f"{price_condition.lower()} {warning_price}."
                    )
                    await bot.send_message(chat_id=chat_id, text=message)
                    delete_alert(alert_id)
            if 'Less than' == price_condition:
                print(f'Current price:{current_price} Warning price:{int(warning_price)}')
                if int(warning_price) >= current_price:
                    message = (
                    f"Alert! The price of {cryptocurrency.capitalize()} is now "
                    f"{price_condition.lower()} {warning_price}."
                    )
                    await bot.send_message(chat_id=chat_id, text=message)
                    delete_alert(alert_id)

if __name__ == '__main__':
    my_thread = threading.Thread(target=lambda: asyncio.run(send_reminders()), daemon=True)
    my_thread.start()
    app.run_polling()