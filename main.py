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
    

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    if message.document:
        file = message.document
        mime_type = file.mime_type
        file_name = file.file_name
        
        print(f"Received document: {file_name} ({mime_type})")
        
        if mime_type == 'application/pdf':
            await message.reply_text("Processing your PDF document...")
            # Add PDF processing logic here
        elif mime_type.startswith('text/'):
            await message.reply_text("Processing your text document...")
            # Add text file processing logic here
        else:
            await message.reply_text("Sorry, I can only process PDF and text documents at the moment.")
            
    elif message.photo:
        photo = message.photo[-1]  # Get the largest photo size
        print(f"Received photo with file_id: {photo.file_id}")
        await message.reply_text("Processing your image...")
        # Add image processing logic here
        
    elif message.voice or message.audio:
        file = message.voice or message.audio
        print(f"Received audio file with file_id: {file.file_id}")
        await message.reply_text("Processing your audio file...")
        # Add audio processing logic here
        
    else:
        await message.reply_text("Sorry, I don't recognize this type of file.")

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
    
    #files
    app.add_handler(MessageHandler(
        filters.PHOTO | 
        filters.AUDIO | 
        filters.VOICE | 
        filters.Document.ALL, 
        handle_file
    ))

    #errors
    app.add_error_handler(error_handler)

    #polls the bot
    print("...polling")
    app.run_polling(poll_interval=3)