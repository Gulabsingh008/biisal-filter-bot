from pyrogram import Client, filters
import os
import subprocess
import yt_dlp

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

    start_time = int(duration / 2) - 30

    cmd = f"ffmpeg -i {video_path} -ss {start_time} -t 60 -c copy {output_path}"
    subprocess.run(cmd, shell=True)

    print(f"🎥 Clipping Done: {output_path}")

    await message.reply_video(output_path, caption=f"📁 `{file_name}`")
    await message.reply("✅ Process Completed Successfully!")

    os.remove(video_path)
    os.remove(output_path)


# ✅ YOUTUBE VIDEO DOWNLOAD FEATURE ✅
@Client.on_message(filters.command("yt") & filters.private)
async def download_youtube_video(client, message):
    if len(message.command) < 2:
        await message.reply("🚫 Please provide a YouTube link! Example: `/yt <url>`")
        return

    url = message.command[1]
    await message.reply("📥 Downloading YouTube video...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            file_name = os.path.basename(file_path)
        except Exception as e:
            await message.reply(f"🚫 Error: {e}")
            return

    print(f"✅ YouTube Downloaded: {file_path}")

    await message.reply_video(file_path, caption=f"📁 `{file_name}`")
    await message.reply("✅ YouTube Video Downloaded Successfully!")

    os.remove(file_path)
