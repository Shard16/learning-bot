from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import AsyncClient

TOKEN = "8373204697:AAHXHtC84dXkfamlz2euguB6rX81wv_QzYg"

BOT_USERNAME = "@Autonoflow_bot"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your learning bot. How can I assist you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am here to help you learn! You can send me documents or ask questions.")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command response.")


#responses

def handle_response(text: str) -> str:
    if 'hello' in text.lower():
        return "Hello! How can I assist you today?"
    elif 'help' in text.lower():
        return "I am here to help you learn! You can send me documents or ask questions."
    elif 'how are you' in text.lower():
        return "I a fine." 
    else:
        return "I'm sorry, I didn't understand that."
    

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat_id}) in Message type: {message_type} - Text: {text}")

    response = handle_response(text)

    print("bot response: ", response)
    await update.message.reply_text(response)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")



if __name__ == "__main__":
    print("...starting bot")
    app = ApplicationBuilder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))

    #messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    #errors
    app.add_error_handler(error_handler)

    #polls the bot
    print("...polling")
    app.run_polling(poll_interval=3)