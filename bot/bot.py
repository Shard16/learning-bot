import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import AsyncClient

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a PDF to get started.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save the file and forward to backend
    file = await update.message.document.get_file()
    path = f"/tmp/{file.file_id}.pdf"
    await file.download_to_drive(path)
    async with AsyncClient() as client:
        # upload logic here
        await client.post(f"{BACKEND_URL}/upload_pdf")
    await update.message.reply_text("PDF received. Processing...")

def run():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()

if __name__ == "__main__":
    run()
