from pyrogram import filters, Client
import bs4, requests, re, asyncio
import os, traceback, random
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

        if '/reel/' in link:  # Handling Reels
            meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
            if meta_tag.ok:
                res = meta_tag.json()
                meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                content_value = meta[0]
            else:
                return await message.reply("Oops something went wrong")

            try:
                dump_file = await message.reply_video(content_value, caption="Download By 👉 @af")
            except Exception as e:
                downfile = f"{os.getcwd()}/{random.randint(1, 10000000)}"
                with open(downfile, 'wb') as x:
                    x.write(requests.get(content_value, headers=headers).content)
                dump_file = await message.reply_video(downfile, caption="Download By 👉 @af")

        elif '/p/' in link:  # Handling Posts
            meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
            if meta_tag.ok:
                res = meta_tag.json()
                meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
            else:
                return await message.reply("Oops something went wrong")

            for i in range(len(meta) - 1):
                com = await message.reply_text(meta[i])
                await asyncio.sleep(1)
                try:
                    dump_file = await message.reply_video(com.text, caption="Download By 👉 @af")
                    await com.delete()
                except:
                    pass

        elif "stories" in link:  # Handling Stories
            meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
            if meta_tag.ok:
                res = meta_tag.json()
                meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
            else:
                return await message.reply("Oops something went wrong")

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
