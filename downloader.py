Podangu, [03-04-2025 03:45]
import os
from pytubefix import YouTube, request
from tqdm import tqdm
import subprocess
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

# Configuration
request.default_range_size = 1048576
progress_bar = None
TOKEN = "6991024540:AAHkfv6aLJPt91NzHmPaj6I4Q9F0E_ZGNK8"  # Replace with your bot token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "🎵 Welcome to Media Downloader Bot!\n\n"
        "Send me YouTube or Spotify links and I'll download them for you.\n\n"
        "Supported services:\n"
        "- YouTube (including Music)\n"
        "- Spotify"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "📝 How to use this bot:\n\n"
        "1. Send a YouTube/Spotify link (single link per message)\n"
        "2. Wait for the download to complete\n"
        "3. Receive your media file\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - This help message"
    )

def on_progress(video_stream, data_chunk, bytes_remaining):
    global progress_bar
    current_downloaded = video_stream.filesize - bytes_remaining
    progress_update = current_downloaded - progress_bar.n
    progress_bar.update(progress_update)

async def download_youtube(update: Update, video_url):
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        highest_res_stream = yt.streams.get_highest_resolution()
        
        global progress_bar
        progress_bar = tqdm(
            total=highest_res_stream.filesize,
            unit='B',
            unit_scale=True,
            desc=yt.title[:15]
        )
        
        await update.message.reply_text(f"⬇️ Downloading: {yt.title}")
        file_path = highest_res_stream.download()
        progress_bar.close()
        
        # Send the downloaded file
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=InputFile(video_file),
                caption=f"✅ {yt.title}"
            )
        
        # Clean up
        os.remove(file_path)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error downloading YouTube video: {e}")
        logger.error(f"YouTube download error: {e}")

async def download_spotify(update: Update, spotify_url):
    try:
        await update.message.reply_text(f"🎵 Downloading from Spotify...")
        
        # Download using spotdl
        result = subprocess.run(["spotdl", spotify_url], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find the downloaded file (spotdl downloads in current directory)
            downloaded_files = [f for f in os.listdir() if f.endswith(('.mp3', '.m4a'))]
            
            if downloaded_files:
                latest_file = max(downloaded_files, key=os.path.getctime)
                with open(latest_file, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=InputFile(audio_file),
                        caption="✅ Spotify download complete"
                    )
                os.remove(latest_file)
            else:
                await update.message.reply_text("❌ Downloaded file not found")
        else:
            await update.message.reply_text(f"❌ Spotify download failed: {result.stderr}")
            logger.error(f"Spotify download error: {result.stderr}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error downloading from Spotify: {e}")
        logger.error(f"Spotify download error: {e}")

Podangu, [03-04-2025 03:45]
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages containing URLs."""
    message_text = update.message.text.strip()
    
    if not message_text:
        await update.message.reply_text("Please send a valid YouTube or Spotify URL")
        return
    
    if "youtube.com" in message_text or "youtu.be" in message_text or "music.youtube.com" in message_text:
        await download_youtube(update, message_text)
    elif "spotify.com" in message_text:
        await download_spotify(update, message_text)
    else:
        await update.message.reply_text("⚠️ Unsupported link. Please send a YouTube or Spotify URL.")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - handle the message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
