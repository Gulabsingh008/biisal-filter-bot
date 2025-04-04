from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
import asyncio
import pymongo

# ✅ MongoDB Connection
MONGO_URL = "mongodb+srv://kuldiprathod2003:kuldiprathod2003@cluster0.wxqpikp.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URL)
db = client["TelegramBots"]
users_collection = db["users"]

# ✅ Multiple Bot Tokens Yahan Add Karo
bot_tokens = [
    "8152839871:AAFq4rA-s3bH4iLMxYTYretkpnzmjfUaSxQ",
    "7306435236:AAEJSqc22sHqJ7G2UbQ4DoT0X7kFgCKgyho",
    "8152839871:AAFq4rA-s3bH4iLMxYTYretkpnzmjfUaSxQ"
]

# ✅ Bots और Dispatchers List
bots = []
dispatchers = []

# ✅ /start Handler (Async Handler Function)
async def start_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    bot_username = (await bot.get_me()).username

    # ✅ Save User to DB if Not Exists
    if not users_collection.find_one({"user_id": user_id, "bot_username": bot_username}):
        users_collection.insert_one({"user_id": user_id, "bot_username": bot_username})
    
    await message.answer(f"👋 Hello {message.from_user.first_name}, this is @{bot_username}!")

# ✅ Broadcast Handler
async def broadcast_handler(message: types.Message, bot: Bot):
    if message.from_user.id != 123456789:  # ✅ Replace with your Telegram ID
        return await message.reply("🚫 Not Authorized")

    text = message.text.replace("/broadcast ", "")
    sent = 0
    bot_username = (await bot.get_me()).username
    users = users_collection.find({"bot_username": bot_username})

    for user in users:
        try:
            await bot.send_message(user['user_id'], text)
            sent += 1
        except:
            pass
    
    await message.reply(f"✅ Sent to {sent} users")

# ✅ Register Handlers per Bot
def register_bot(token):
    bot = Bot(token=token, parse_mode="HTML")
    dp = Dispatcher(bot)

    dp.register_message_handler(lambda msg: start_handler(msg, bot), commands=['start'])
    dp.register_message_handler(lambda msg: broadcast_handler(msg, bot), commands=['broadcast'])

    bots.append(bot)
    dispatchers.append(dp)

# ✅ Start All Bots Together
async def start_all():
    await asyncio.gather(*(dp.start_polling() for dp in dispatchers))

# ✅ Main
if __name__ == "__main__":
    for token in bot_tokens:
        try:
            register_bot(token)
        except Exception as e:
            print(f"❌ Failed to register bot {token[:10]}...: {e}")
    asyncio.run(start_all())
