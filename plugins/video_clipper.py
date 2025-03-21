import os
import logging
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔥 लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)

# 📌 Temporary Directory
TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# 📌 FFmpeg क्लिपिंग फंक्शन
async def create_clip(input_file, output_file, start_time="00:10:00", duration="30"):
    try:
        logging.info(f"🎬 Clipping Video: {input_file} -> {output_file}")
        command = [
            "ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-t", duration,
            "-c", "copy", output_file
        ]
        subprocess.run(command, check=True)
        logging.info("✅ Clip Created Successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg Error: {e}")
        return False

# 📌 Video Handler
@Client.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    try:
        # 🔥 Step 1: Download Video (Original Name से)
        logging.info("📥 Downloading video...")
        file_name = message.video.file_name if message.video.file_name else f"{message.video.file_id}.mp4"
        input_path = os.path.join(TEMP_DIR, file_name)
        output_path = os.path.join(TEMP_DIR, f"clip_{file_name}")

        await client.download_media(message.video, file_name=input_path)

        # 🎬 Step 2: Create Clip
        if await create_clip(input_path, output_path):
            # 🚀 Step 3: Send Clipped Video
            logging.info("📤 Sending clipped video...")
            await client.send_video(chat_id=message.chat.id, video=open(output_path, "rb"))
        else:
            await message.reply("⚠️ Clipping failed. Try another video.")

        # 🧹 Cleanup
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        await message.reply("⚠️ An error occurred. Please try again.")
