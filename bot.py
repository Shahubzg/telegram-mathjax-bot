import re
import logging
import pandas as pd
import tempfile
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8080352149:AAEPo-tmMoN8vjQWkb4L7tvjkj9hMgJ6CGM"

def convert_mathjax(text):
    if not isinstance(text, str):
        return text
    return re.sub(r'\$(.+?)\$', r'\\(\1\\)', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a CSV and I’ll convert all $...$ into \\( ... \\)."
    )

async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document

    if not file.file_name.endswith(".csv"):
        await update.message.reply_text("Please send a CSV file.")
        return

    # ---- Create a safe temp file for download ----
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_input:
        input_path = Path(temp_input.name)

    telegram_file = await file.get_file()
    await telegram_file.download_to_drive(str(input_path))

    # Load CSV
    df = pd.read_csv(input_path)

    # Convert
    df = df.applymap(convert_mathjax)

    # ---- Create safe output file ----
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_output:
        output_path = Path(temp_output.name)

    df.to_csv(output_path, index=False)

    # Send file back
    await update.message.reply_document(
        document=open(output_path, "rb"),
        filename=f"converted_{file.file_name}"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("text/csv"), handle_csv))

    print("Bot is running...")
    app.run_polling()