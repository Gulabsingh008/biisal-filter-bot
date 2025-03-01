import aiohttp
import asyncio
import os
import re
import traceback
import random
from pyrogram import Client, filters
from info import LOG_CHANNEL as DUMP_GROUP

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://saveig.app",
    "Connection": "keep-alive",
    "Referer": "https://saveig.app/en",
}

@Client.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.private)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    try:
        m = await message.reply_sticker("CAACAgUAAxkBAAKD6mcTLETIv8Yrc83GnIcYXP9Ip6LHAAKgCQACJ_YYVbZRplnJDKrJNgQ")

        async with aiohttp.ClientSession() as session:
            async with session.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers) as response:
                if response.status == 200:
                    res = await response.json()
                    meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                    if not meta:
                        return await message.reply("Oops something went wrong")
                    content_value = meta[0]
                else:
                    return await message.reply("Oops something went wrong")

            if '/reel/' in link:  # Handling Reels
                try:
                    dump_file = await message.reply_video(content_value, caption="Download By 👉 @af")
                except Exception as e:
                    downfile = f"{os.getcwd()}/{random.randint(1, 10000000)}"
                    async with session.get(content_value, headers=headers) as resp:
                        with open(downfile, 'wb') as f:
                            f.write(await resp.read())
                    dump_file = await message.reply_video(downfile, caption="Download By 👉 @af")

            elif '/p/' in link:  # Handling Posts
                for i in range(len(meta) - 1):
                    com = await message.reply_text(meta[i])
                    await asyncio.sleep(1)
                    try:
                        dump_file = await message.reply_video(com.text, caption="Download By 👉 @af")
                        await com.delete()
                    except:
                        pass

            elif "stories" in link:  # Handling Stories
                try:
                    dump_file = await message.reply_video(meta[0], caption="Download By 👉 @af")
                except:
                    com = await message.reply(meta[0])
                    await asyncio.sleep(1)
                    try:
                        dump_file = await message.reply_video(com.text, caption="Download By 👉 @af")
                        await com.delete()
                    except:
                        pass

        if 'dump_file' in locals():
            await dump_file.forward(DUMP_GROUP)

        await m.delete()

    except Exception as e:
        try:
            await message.reply(f"400: Sorry, Unable To Find It Make Sure It's Publicly Available :)")
        except Exception as e:
            if DUMP_GROUP:
                await Mbot.send_message(DUMP_GROUP, f"Instagram Error: {e} {link}")
                await Mbot.send_message(DUMP_GROUP, traceback.format_exc())
            await message.reply(f"400: Sorry, Unable To Find It. Try another or report it to @af")

    finally:
        if 'dump_file' in locals():
            if DUMP_GROUP:
                await dump_file.copy(DUMP_GROUP)
        await m.delete()
        if 'downfile' in locals():
            os.remove(downfile)
        await message.reply("<a href='https://t.me/af'>af</a>")
