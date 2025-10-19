from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import AsyncClient

import os
import threading
import tempfile
from flask import Flask, request, jsonify

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8373204697:AAHXHtC84dXkfamlz2euguB6rX81wv_QzYg")

BOT_USERNAME = os.getenv("BOT_USERNAME", "@Autonoflow_bot")

# Backend endpoint where the bot will POST uploaded documents for processing
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")
# Callback server settings - backend will POST results here after processing
CALLBACK_HOST = os.getenv("CALLBACK_HOST", "0.0.0.0")
CALLBACK_PORT = int(os.getenv("CALLBACK_PORT", "8080"))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command.

        This function is called when the user sends the /start command to the bot.
        It sends a short greeting and brief instruction on how to use the bot.

        Parameters
        - update: telegram.Update - contains incoming update and message metadata
        - context: telegram.ext.ContextTypes.DEFAULT_TYPE - context with bot data and helper methods

        Notes
        - This handler is intentionally simple. Later we may add onboarding steps,
            persistent user records, or deep-link handling.
        """
        # Reply with a friendly message that introduces the bot.
        await update.message.reply_text("Hello! I am your learning bot. How can I assist you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command.

    Provide short usage instructions. Keep this message concise because it is
    typically displayed in chat; for longer docs we could link to a web page.
    """
    await update.message.reply_text("I am here to help you learn! You can send me documents or ask questions.")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder for a custom command.

    Use this as an example to add other bot commands (e.g. /quiz, /summary, /subscribe).
    """
    await update.message.reply_text("This is a custom command response.")


#responses

def handle_response(text: str) -> str:
    """Very small text-response router used as an example.

    This function demonstrates a simple rule-based reply engine. In production
    this should be replaced with either:
      - a natural language understanding module (intent/entity extractor), or
      - a call to a conversational LLM with safety and rate-limiting.

    Edge cases:
      - `text` may be None (message without text). Callers should ensure text is str.
      - Matchings are naive and case-insensitive; more robust matching is recommended.
    """
    if not text:
        # Defensive: if no text provided, return a fallback message.
        return "I didn't receive any text. Send me a message or a document."

    text_lower = text.lower()
    if 'hello' in text_lower:
        return "Hello! How can I assist you today?"
    elif 'help' in text_lower:
        return "I am here to help you learn! You can send me documents or ask questions."
    elif 'how are you' in text_lower:
        # small intentional typo present in original; keep simple reply
        return "I a fine."
    else:
        # Default fallback when the simple rules do not match
        return "I'm sorry, I didn't understand that."
    

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id
    # The bot can receive several kinds of file-like content from users:
    #  - message.document: files sent as "document" (e.g. PDF, txt)
    #  - message.photo: images (array of sizes)
    #  - message.voice or message.audio: voice notes or audio files
    # For each case we download the file locally (into a NamedTemporaryFile),
    # then upload it to a backend service for heavier processing (PDF parsing,
    # OCR, transcription, summarization, embedding generation, etc.).

    if message.document:
        # Documents include PDFs, Word docs, text files, etc.
        file = message.document
        mime_type = file.mime_type
        file_name = file.file_name

        # Log basic info for debugging
        print(f"Received document: {file_name} ({mime_type})")

        # PDF handling: we send PDFs to /upload_pdf endpoint on the backend.
        if mime_type == 'application/pdf':
            await message.reply_text("Processing your PDF document...")
            # Download the file content to a temporary file on disk and then POST
            # the binary to the backend. We keep the file on disk (delete=False)
            # so developers can inspect it if needed; in production you'd delete it
            # or upload directly to object storage.
            file_obj = await file.get_file()
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                # download_to_drive writes the content to the given path
                await file_obj.download_to_drive(tmp.name)
                tmp_path = tmp.name

            # Use httpx AsyncClient to upload the file to the backend service.
            async with AsyncClient() as client:
                with open(tmp_path, 'rb') as fh:
                    files = {'file': (file_name, fh, mime_type)}
                    data = {'chat_id': chat_id, 'file_name': file_name}
                    try:
                        resp = await client.post(f"{BACKEND_URL}/upload_pdf", files=files, data=data, timeout=60.0)
                        if resp.status_code == 200:
                            await message.reply_text("Uploaded PDF to processing backend. You'll receive results when ready.")
                        else:
                            # Backend returned an error status; inform the user
                            await message.reply_text("Failed to upload PDF to backend.")
                    except Exception as e:
                        # Network or other client-side error
                        await message.reply_text("Error uploading PDF to backend: {}".format(str(e)))

        # Text files: send to a separate endpoint so backend can use fast text parsing
        elif mime_type.startswith('text/'):
            await message.reply_text("Processing your text document...")
            file_obj = await file.get_file()
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                await file_obj.download_to_drive(tmp.name)
                tmp_path = tmp.name
            async with AsyncClient() as client:
                with open(tmp_path, 'rb') as fh:
                    files = {'file': (file_name, fh, mime_type)}
                    data = {'chat_id': chat_id, 'file_name': file_name}
                    try:
                        resp = await client.post(f"{BACKEND_URL}/upload_text", files=files, data=data, timeout=30.0)
                        if resp.status_code == 200:
                            await message.reply_text("Uploaded text file to processing backend. You'll receive results when ready.")
                        else:
                            await message.reply_text("Failed to upload text file to backend.")
                    except Exception as e:
                        await message.reply_text("Error uploading text file to backend: {}".format(str(e)))
        else:
            # Unknown document MIME type — inform the user and list supported types
            await message.reply_text("Sorry, I can only process PDF and text documents at the moment.")

    elif message.photo:
        # Photos arrive as a list of PhotoSize objects; pick the largest for best quality
        photo = message.photo[-1]
        print(f"Received photo with file_id: {photo.file_id}")
        await message.reply_text("Processing your image...")

        # Download and upload image to backend; backend may run OCR or classification
        file_obj = await photo.get_file()
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            await file_obj.download_to_drive(tmp.name)
            tmp_path = tmp.name
        async with AsyncClient() as client:
            with open(tmp_path, 'rb') as fh:
                files = {'file': ('image.jpg', fh, 'image/jpeg')}
                data = {'chat_id': chat_id}
                try:
                    resp = await client.post(f"{BACKEND_URL}/upload_image", files=files, data=data, timeout=30.0)
                    if resp.status_code == 200:
                        await message.reply_text("Uploaded image to backend for processing.")
                    else:
                        await message.reply_text("Failed to upload image to backend.")
                except Exception as e:
                    await message.reply_text("Error uploading image to backend: {}".format(str(e)))

    elif message.voice or message.audio:
        # Voice messages are short OGGs; audio may be longer files
        file = message.voice or message.audio
        print(f"Received audio file with file_id: {file.file_id}")
        await message.reply_text("Processing your audio file...")

        # Download and upload audio to backend. Backend should transcribe and/or
        # run audio summarization; choose appropriate timeout for longer files.
        file_obj = await file.get_file()
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            await file_obj.download_to_drive(tmp.name)
            tmp_path = tmp.name
        async with AsyncClient() as client:
            with open(tmp_path, 'rb') as fh:
                files = {'file': ('audio.ogg', fh, 'audio/ogg')}
                data = {'chat_id': chat_id}
                try:
                    resp = await client.post(f"{BACKEND_URL}/upload_audio", files=files, data=data, timeout=60.0)
                    if resp.status_code == 200:
                        await message.reply_text("Uploaded audio to backend for processing.")
                    else:
                        await message.reply_text("Failed to upload audio to backend.")
                except Exception as e:
                    await message.reply_text("Error uploading audio to backend: {}".format(str(e)))

    else:
        # The message didn't contain any file-like object we recognize
        await message.reply_text("Sorry, I don't recognize this type of file.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat_id}) in Message type: {message_type} - Text: {text}")

    response = handle_response(text)

    print("bot response: ", response)
    await update.message.reply_text(response)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler for the application.

    The telegram.ext library calls this handler when an exception bubbles up from
    a handler. Here we simply log the error to stdout. In production, consider
    sending the error to an observability system (Sentry, Datadog) and notifying
    the developer or ops team if critical.
    """
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