import os
import re
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext import CallbackContext
from dotenv import load_dotenv

# Load the token from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Regular expressions to match video and thumbnail URLs
video_regex = re.compile(r'https://xhamster\.com/videos/[^"]+')
thumbnail_regex = re.compile(r'https://ic-vt-nss\.xhcdn\.com/[^"]+')

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me an HTML file, and I'll extract video and thumbnail URLs for you.")

# Handler for file uploads
def handle_file(update: Update, context: CallbackContext):
    try:
        file = update.message.document.get_file()
        file_content = BytesIO(file.download_as_bytearray()).read().decode('utf-8')  # Download the file in-memory and decode

        # Find all video and thumbnail links
        video_links = video_regex.findall(file_content)
        thumbnail_links = thumbnail_regex.findall(file_content)

        # Remove duplicates while maintaining order
        video_links = list(dict.fromkeys(video_links))
        thumbnail_links = list(dict.fromkeys(thumbnail_links))

        if not video_links:
            update.message.reply_text("No video links found.")
            return

        # Prepare response
        response = "Here are the extracted links:\n\n"
        for video_link, thumbnail_link in zip(video_links, thumbnail_links):
            response += f"Video: {video_link}\nThumbnail: {thumbnail_link}\n\n"

        update.message.reply_text(response)

    except Exception as e:
        update.message.reply_text("An error occurred while processing your file.")
        print(f"Error: {e}")

# Error handler
def error_handler(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")
    update.message.reply_text('An error occurred.')

def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the /start command
    dp.add_handler(CommandHandler("start", start))

    # Register the message handler for document uploads
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/html"), handle_file))

    # Log all errors
    dp.add_error_handler(error_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl+C is pressed
    updater.idle()

if __name__ == '__main__':
    main()
