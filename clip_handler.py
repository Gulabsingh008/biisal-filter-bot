from pyrogram import Client, filters
import os
import random
import subprocess

CLIP_DIR = "clips"
os.makedirs(CLIP_DIR, exist_ok=True)

@Client.on_message(filters.command("clip") & filters.private)
async def clip_command(client, message):
    await message.reply("📩 Send a video to extract a 60-sec random clip.")

@Client.on_message(filters.video & filters.private)
async def process_video(client, message):
    if not message.video:
        await message.reply("कृपया एक वीडियो भेजें!")
        return

    # वीडियो डाउनलोड करें
    video_path = await message.download()
    clip_filename = os.path.join(CLIP_DIR, f"clip_{random.randint(1000, 9999)}.mp4")

    # Debugging Message
    print(f"✅ Video Received: {video_path}")

    # FFmpeg से वीडियो की Duration निकालें
    duration_cmd = f"ffprobe -i \"{video_path}\" -show_entries format=duration -v quiet -of csv=\"p=0\""
    duration_output = subprocess.getoutput(duration_cmd)

    try:
        duration = float(duration_output.strip())
    except ValueError:
        await message.reply("🚫 Error: Unable to get video duration!")
        return

    if duration < 60:
        await message.reply("वीडियो 60 सेकंड से छोटा है!")
        os.remove(video_path)  # Unused file delete करें
        return

    # वीडियो के बीच से 60 सेकंड की क्लिप निकालने के लिए Start Time सेट करें
    start_time = max(0, int(duration / 2) - 30)  

    # FFmpeg Command to Extract 60-sec Clip
    cmd = f"ffmpeg -i \"{video_path}\" -ss {start_time} -t 60 -c copy \"{clip_filename}\""
    subprocess.run(cmd, shell=True, check=True)

    # Debugging Message
    print(f"🎥 Clipping Done: {clip_filename}")

    # अब बॉट क्लिप भेजेगा
    await message.reply_video(clip_filename, caption="🎥 Here is your 60-sec sample clip!")

    # Debugging Message
    print("✅ Clip Sent Successfully!")

    # क्लिप और ओरिजिनल वीडियो को डिलीट करें
    os.remove(video_path)
    os.remove(clip_filename)
