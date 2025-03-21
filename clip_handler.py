import os
import json
import subprocess
from pyrogram import Client, filters

CLIP_DIR = "clips"
os.makedirs(CLIP_DIR, exist_ok=True)

def get_video_duration(video_path):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception as e:
        print(f"🚫 Error in ffprobe: {e}")
        return None  

@Client.on_message(filters.video & filters.private)
async def process_video(client, message):
    if not message.video:
        await message.reply("कृपया एक वीडियो भेजें!")
        return

    video_path = await message.download()
    print(f"✅ Video Received: {video_path}")

    duration = get_video_duration(video_path)
    
    if duration is None:
        await message.reply("🚫 Error: Unable to get video duration!")
        return

    if duration < 60:
        await message.reply("वीडियो 60 सेकंड से छोटा है!")
        return

    start_time = int(duration / 2) - 30  
    output_path = f"clip_{os.path.basename(video_path)}"

    cmd = f"ffmpeg -i {video_path} -ss {start_time} -t 60 -c copy {output_path}"
    subprocess.run(cmd, shell=True)

    print(f"🎥 Clipping Done: {output_path}")
    await message.reply_video(output_path, caption=f"🎬 Here is your sample: `{os.path.basename(output_path)}`")

    os.remove(video_path)
    os.remove(output_path)
