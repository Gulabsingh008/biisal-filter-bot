from pyrogram import Client, filters
import os
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

    video_path = await message.download()
    file_name = os.path.basename(video_path)  # Extract only the filename
    output_path = f"clip_{file_name}"

    print(f"✅ Video Received: {video_path}")

    # Get video duration
    duration_cmd = f"ffprobe -i {video_path} -show_entries format=duration -v quiet -of csv='p=0'"
    duration_output = subprocess.getoutput(duration_cmd)

    try:
        duration = float(duration_output)
    except ValueError:
        await message.reply("🚫 Error: Unable to get video duration!")
        return

    if duration < 60:
        await message.reply("🚫 Error: Video is shorter than 60 seconds!")
        return

    start_time = int(duration / 2) - 30  # वीडियो के बीच से 60 सेकंड निकालने के लिए

    cmd = f"ffmpeg -i {video_path} -ss {start_time} -t 60 -c copy {output_path}"
    subprocess.run(cmd, shell=True)

    print(f"🎥 Clipping Done: {output_path}")

    await message.reply_video(output_path, caption=f"📁 `{file_name}`")
    await message.reply("✅ Process Completed Successfully!")

    os.remove(video_path)
    os.remove(output_path)
