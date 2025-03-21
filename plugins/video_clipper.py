import os
import logging
import subprocess
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔥 लॉगिंग सेटअप
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs.txt"),  # ✅ Logs को File में Save करेंगे
        logging.StreamHandler()
    ]
)

# 📌 Temporary Directory
TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# ✅ Chunk Size for Faster Download
CHUNK_SIZE = 512 * 1024  # 512 KB

# 📌 FFmpeg क्लिपिंग फंक्शन (Optimized)
async def create_clip(input_file, output_file, start_time="00:10:00", duration="30"):
    try:
        logging.info(f"🎬 Clipping Video: {input_file} -> {output_file}")
        start = time.time()
        
        command = [
            "ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-t", duration,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", output_file
        ]
        subprocess.run(command, check=True)

        end = time.time()
        logging.info(f"✅ Clip Created Successfully in {round(end - start, 2)} seconds!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg Error: {e}")
        return False

# 📌 Download Progress Callback Function
async def progress(current, total):
    percent = round((current / total) * 100, 2)
    logging.info(f"⬇️ Downloading... {percent}% Completed")

# 📌 Optimized Video Download Function
async def download_video(client: Client, message: Message, save_path: str):
    logging.info("📥 Downloading video...")
    start = time.time()

    try:
        await client.download_media(
            message.video,
            file_name=save_path,
            progress=progress  # ✅ Progress को Log करेंगे
        )

        end = time.time()
        logging.info(f"✅ Download Completed in {round(end - start, 2)} seconds!")
        return True
    except Exception as e:
        logging.error(f"❌ Download Error: {e}")
        return False

# 📌 Optimized Video Upload Function
async def upload_video(client: Client, chat_id: int, file_path: str, caption: str):
    logging.info("📤 Uploading video...")
    start = time.time()

    try:
        await client.send_video(
            chat_id=chat_id,
            video=file_path,
            caption=caption,
            supports_streaming=True
        )

        end = time.time()
        logging.info(f"✅ Upload Completed in {round(end - start, 2)} seconds!")
        return True
    except Exception as e:
        logging.error(f"❌ Upload Error: {e}")
        return False

# 📌 Video Handler
@Client.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    try:
        file_name = message.video.file_name if message.video.file_name else f"{message.video.file_id}.mp4"
        input_path = os.path.join(TEMP_DIR, file_name)
        output_path = os.path.join(TEMP_DIR, f"clip_{file_name}")

        # 🔥 Step 1: Download with Progress
        if not await download_video(client, message, input_path):
            await message.reply("⚠️ Download failed. Please try again.")
            return

        # 🎬 Step 2: Create Clip
        if not await create_clip(input_path, output_path):
            await message.reply("⚠️ Clipping failed. Try another video.")
            return

        # 🚀 Step 3: Upload with Progress
        caption = message.caption if message.caption else "🎬 Clipped Video"
        if not await upload_video(client, message.chat.id, output_path, caption):
            await message.reply("⚠️ Upload failed. Please try again.")
            return

        # 🧹 Cleanup
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        logging.error(f"❌ Main Error: {e}")
        await message.reply("⚠️ An error occurred. Please check logs.txt")
