import os
import asyncio
import logging
import random
import subprocess
from pyrogram import Client
from pyrogram.types import Message

# लॉग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FFmpeg से वीडियो की लंबाई (ड्यूरेशन) निकालने का फ़ंक्शन
async def get_video_duration(video_path):
    try:
        cmd = [
            "ffprobe", "-i", video_path,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0"
        ]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"FFprobe Error: {stderr.decode()}")
            return None
        return float(stdout.decode().strip())  # ड्यूरेशन सेकंड में लौटाएँ
    except Exception as e:
        logger.error(f"Error in fetching duration: {str(e)}")
        return None

# FFmpeg से रैंडम क्लिप बनाने का फ़ंक्शन
async def clip_video(input_file, output_file, start_time, duration):
    try:
        cmd = [
            "ffmpeg", "-i", input_file,
            "-ss", start_time, "-t", duration,
            "-c", "copy", output_file
        ]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg Error: {stderr.decode()}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error in clipping video: {str(e)}")
        return False

# वीडियो प्रोसेस करने का हैंडलर
async def process_video(client: Client, message: Message):
    if not message.video:
        await message.reply_text("❌ कोई वीडियो फ़ाइल नहीं मिली!")
        return

    video_path = await client.download_media(message.video)
    if not os.path.exists(video_path):
        await message.reply_text("❌ फ़ाइल डाउनलोड करने में समस्या हुई!")
        return

    file_name = os.path.basename(video_path)
    safe_file_name = file_name.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace(" ", "_")
    output_path = f"/app/clips/clip_{safe_file_name}"

    # वीडियो की कुल लंबाई निकालें
    video_duration = await get_video_duration(video_path)
    if not video_duration:
        await message.reply_text("❌ वीडियो की लंबाई पता करने में समस्या हुई!")
        return

    # 30 सेकंड की क्लिपिंग के लिए रैंडम स्टार्ट टाइम सेट करें
    if video_duration > 30:
        random_start = random.randint(0, int(video_duration) - 30)
    else:
        random_start = 0  # अगर वीडियो छोटा है, तो स्टार्ट 0 से करें

    start_time = f"00:{random_start//60:02}:{random_start%60:02}"  # HH:MM:SS फॉर्मेट में
    duration = "00:00:30"  # 30 सेकंड की क्लिप बनाएँ

    await message.reply_text(f"🎥 रैंडम क्लिपिंग शुरू हो रही है: `{file_name}`\n⏳ स्टार्ट टाइम: {start_time}")

    success = await clip_video(video_path, output_path, start_time, duration)
    if not success:
        await message.reply_text("❌ वीडियो क्लिपिंग में समस्या हुई!")
        return

    await message.reply_video(output_path, caption=f"🎬 Here is your random clip: `{os.path.basename(output_path)}`\n⏳ Start Time: {start_time}")
    os.remove(video_path)  # असली वीडियो हटाएँ
    os.remove(output_path)  # क्लिप हटाएँ
