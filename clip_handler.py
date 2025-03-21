from pyrogram import Client, filters
import random
import os
import subprocess

CLIP_DIR = "clips"
os.makedirs(CLIP_DIR, exist_ok=True)

@Client.on_message(filters.command("clip") & filters.private)
async def clip_command(client, message):
    await message.reply("📩 Send a video to extract a 60-sec random clip.")

@Client.on_message(filters.video & filters.private)
import subprocess

async def process_video(client, message):
    if not message.video:
        await message.reply("कृपया एक वीडियो भेजें!")
        return

    video_path = await message.download()
    output_path = f"sample_{video_path}"

    # Debugging Message
    print(f"✅ Video Received: {video_path}")

    # FFmpeg Command to Extract 60-sec Clip from Middle
    duration_cmd = f"ffprobe -i {video_path} -show_entries format=duration -v quiet -of csv='p=0'"
    duration = float(subprocess.getoutput(duration_cmd))
    
    if duration < 60:
        await message.reply("वीडियो 60 सेकंड से छोटा है!")
        return

    start_time = int(duration / 2) - 30  # वीडियो के बीच से 60 सेकंड निकालने के लिए

    cmd = f"ffmpeg -i {video_path} -ss {start_time} -t 60 -c copy {output_path}"
    subprocess.run(cmd, shell=True)

    # Debugging Message
    print(f"🎥 Clipping Done: {output_path}")

    # अब बॉट क्लिप भेजेगा
    await message.reply_video(output_path, caption="Here is your 60-sec sample clip!")

    # Debugging Message
    print("✅ Clip Sent Successfully!")

    with open(clip_filename, "rb") as clip:
        await message.reply_video(clip, caption="🎥 Here is your 60-sec sample clip!")

    os.remove(file_path)
    os.remove(clip_filename)
