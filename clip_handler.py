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
async def process_video(client, message):
    video = message.video
    file_id = video.file_id
    file_path = f"{CLIP_DIR}/original_{file_id}.mp4"

    await client.download_media(video, file_path)

    duration_cmd = f'ffprobe -i "{file_path}" -show_entries format=duration -v quiet -of csv="p=0"'
    duration = float(subprocess.getoutput(duration_cmd))

    if duration < 60:
        await message.reply("⚠️ Video must be longer than 60 seconds!")
        return

    start_time = random.randint(0, int(duration) - 60)
    clip_filename = f"{CLIP_DIR}/sample_{file_id}.mp4"

    ffmpeg_cmd = f'ffmpeg -i "{file_path}" -ss {start_time} -t 60 -c copy "{clip_filename}" -y'
    subprocess.run(ffmpeg_cmd, shell=True)

    with open(clip_filename, "rb") as clip:
        await message.reply_video(clip, caption="🎥 Here is your 60-sec sample clip!")

    os.remove(file_path)
    os.remove(clip_filename)
