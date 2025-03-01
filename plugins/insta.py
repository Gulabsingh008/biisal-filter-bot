import logging
from pyrogram import Client, filters


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.private)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    try:
        m = await message.reply_sticker("CAACAgUAAxkBAAKD6mcTLETIv8Yrc83GnIcYXP9Ip6LHAAKgCQACJ_YYVbZRplnJDKrJNgQ")

        async with aiohttp.ClientSession() as session:
            async with session.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers) as response:
                if response.status == 200:
                    res = await response.json()
                    logger.info(f"API Response: {res}")
                    meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                    if not meta:
                        logger.error("No meta tags found in the response.")
                        return await message.reply("Oops something went wrong")
                    content_value = meta[0]
                else:
                    logger.error(f"API Request Failed: {response.status}")
                    return await message.reply("Oops something went wrong")

            # Rest of the code...

    except Exception as e:
        logger.exception("An error occurred while processing the Instagram link.")
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
