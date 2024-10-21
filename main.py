import os
import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

YOUTUBE_URL_PATTERN = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Надсилаємо заставку
    await update.message.reply_photo('./start.jpg')
    await update.message.reply_text(
        "Привіт! Я бот для завантаження відео з YouTube. "
        "Надішли мені посилання на відео, і я його завантажу."
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # Перевіряємо правильність посилання
    if not YOUTUBE_URL_PATTERN.match(url):
        await update.message.reply_text(
            "Виникла помилка, перевірте правильність посилання. "
            "Воно має бути у форматі https://www.youtube.com/[код_відео]"
        )
        return

    await update.message.reply_text("Завантаження розпочато...")

    try:
        ydl_opts = {
            'format': 'bestvideo[height<=720]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        await update.message.reply_text("Завантаження завершено! Відправляю відео...")

        with open(video_file, 'rb') as video:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)

        os.remove(video_file)

    except yt_dlp.utils.DownloadError:
        await update.message.reply_text(
            "Виникла помилка, перевірте правильність посилання. "
            "Воно має бути у форматі https://www.youtube.com/[код_відео]"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await update.message.reply_text("Сталася невідома помилка. Спробуйте ще раз.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()
