import os
import logging
import subprocess
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔥 लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)

# 📌 Temporary Directory
TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# 📌 Video Chunked Download Function (Corrected)
async def download_video_chunked(client, message, file_path):
    logging.info("📥 Downloading video in chunks...")
    start_time = time.time()

    # 🔥 चंक्स में डाउनलोड करने के लिए `download_media()` का उपयोग करें
    await client.download_media(message, file_name=file_path)

    end_time = time.time()
    logging.info(f"✅ Chunked Download Completed in {round(end_time - start_time, 2)} seconds!")

# 📌 Generate Thumbnail from Video
def generate_thumbnail(video_path, thumb_path):
    try:
        command = [
            "ffmpeg", "-y", "-i", video_path, "-vf", "scale=320:320",
            "-vframes", "1", "-q:v", "2", thumb_path
        ]
        subprocess.run(command, check=True)
        return thumb_path
    except Exception as e:
        logging.error(f"❌ Thumbnail Generation Error: {e}")
        return None

# 📌 Optimized FFmpeg Clipping Function
async def create_clip(input_file, output_file, start_time="00:10:00", duration="30"):
    try:
        logging.info(f"🎬 Clipping & Optimizing Video: {input_file} -> {output_file}")
        start = time.time()

        command = [
            "ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-t", duration,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", "-vf", "scale=-2:720", "-aspect", "16:9",
            output_file
        ]
        subprocess.run(command, check=True)

        end = time.time()
        logging.info(f"✅ Clip Created in {round(end - start, 2)} seconds!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg Error: {e}")
        return False

# 📌 Video Handler
@Client.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    try:
        # 🔥 Step 1: Get File Name
        logging.info("📥 Downloading video in chunks...")
        file_name = message.video.file_name if message.video.file_name else f"{message.video.file_id}.mp4"
        input_path = os.path.join(TEMP_DIR, file_name)
        output_path = os.path.join(TEMP_DIR, f"clip_{file_name}")
        thumb_path = os.path.join(TEMP_DIR, f"thumb_{file_name}.jpg")

        # 🔥 Step 2: Download in Chunks (Fixed)
        await download_video_chunked(client, message, input_path)

        # 🎬 Step 3: Create Clip (Optimized)
        if await create_clip(input_path, output_path):
            # 📸 Step 4: Generate Thumbnail
            generate_thumbnail(output_path, thumb_path)

            # 🚀 Step 5: Send Clipped Video with Custom Thumbnail
            logging.info("📤 Sending clipped video...")
            caption = message.caption if message.caption else "🎬 Clipped Video"
            await client.send_video(
                chat_id=message.chat.id,
                video=output_path,
                thumb=thumb_path,  # ✅ Custom Thumbnail
                caption=caption
            )
        else:
            await message.reply("⚠️ Clipping failed. Try another video.")

        # 🧹 Cleanup
        os.remove(input_path)
        os.remove(output_path)
        os.remove(thumb_path)

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        await message.reply("⚠️ An error occurred. Please try again.")
