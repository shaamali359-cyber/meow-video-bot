import os
import asyncio
import tempfile
from pathlib import Path

import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك 🎬\nأرسل رابط الفيديو لتحميله.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith(("https://", "http://")):
        await update.message.reply_text("أرسل رابطاً صحيحاً.")
        return

    await update.message.reply_text("⏳ جاري تحميل الفيديو...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            options = {
                "format": "best[ext=mp4]/best",
                "outtmpl": str(Path(folder) / "video.%(ext)s"),
                "noplaylist": True,
                "quiet": True
            }

            await asyncio.to_thread(
                lambda: yt_dlp.YoutubeDL(options).download([url])
            )

            files = list(Path(folder).glob("video.*"))

            if not files:
                raise Exception("لم يتم العثور على الفيديو")

            with open(files[0], "rb") as video:
                await update.message.reply_video(video=video)

    except Exception:
        await update.message.reply_text("تعذر تحميل الفيديو. جرّب رابطاً آخر.")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    main()
