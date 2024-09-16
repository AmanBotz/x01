import os
import re
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
    file = update.message.document.get_file()
    file.download('input.html')

    # Open and read the file content
    with open('input.html', 'r', encoding='utf-8') as f:
        file_content = f.read()

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

# Error handler
def error_handler(update: Update, context: CallbackContext):
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
