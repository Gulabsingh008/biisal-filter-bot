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

# 📌 FFmpeg क्लिपिंग फंक्शन (Optimized + Thumbnail Support)
async def create_clip(input_file, output_file, start_time="00:10:00", duration="30", thumbnail_file="thumb.jpg"):
    try:
        logging.info(f"🎬 Clipping Video: {input_file} -> {output_file}")
        start = time.time()
        
        # ✅ FFmpeg Command (Maintain Aspect Ratio)
        command = [
            "ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-t", duration,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-c:a", "aac", "-b:a", "128k",
            "-vf", "scale=-2:720", "-movflags", "+faststart", output_file
        ]
        subprocess.run(command, check=True)

        # ✅ Extract Thumbnail for Telegram
        thumb_cmd = [
            "ffmpeg", "-y", "-i", output_file, "-ss", "00:00:01", "-vframes", "1",
            "-vf", "scale=320:180", thumbnail_file
        ]
        subprocess.run(thumb_cmd, check=True)

        end = time.time()
        logging.info(f"✅ Clip Created Successfully in {round(end - start, 2)} seconds!")
        return thumbnail_file  # Return Thumbnail Path
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg Error: {e}")
        return None

# 📌 Video Handler
@Client.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    try:
        # 🔥 Step 1: Download Video (Original Name से)
        logging.info("📥 Downloading video...")
        start = time.time()
        file_name = message.video.file_name if message.video.file_name else f"{message.video.file_id}.mp4"
        input_path = os.path.join(TEMP_DIR, file_name)
        output_path = os.path.join(TEMP_DIR, f"clip_{file_name}")
        thumbnail_path = os.path.join(TEMP_DIR, "thumb.jpg")

        await client.download_media(message.video, file_name=input_path)
        end = time.time()
        logging.info(f"✅ Download Completed in {round(end - start, 2)} seconds!")

        # 🎬 Step 2: Create Clip (With Thumbnail)
        thumb = await create_clip(input_path, output_path, thumbnail_file=thumbnail_path)
        if thumb:
            # 🚀 Step 3: Send Clipped Video with Thumbnail
            logging.info("📤 Sending clipped video...")
            caption = message.caption if message.caption else "🎬 Clipped Video"
            await client.send_video(
                chat_id=message.chat.id, 
                video=open(output_path, "rb"), 
                caption=caption,
                thumb=thumb
            )
        else:
            await message.reply("⚠️ Clipping failed. Try another video.")

        # 🧹 Cleanup
        os.remove(input_path)
        os.remove(output_path)
        os.remove(thumbnail_path)

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        await message.reply("⚠️ An error occurred. Please try again.")
