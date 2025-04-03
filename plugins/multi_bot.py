from aiogram import Bot, Dispatcher, types, executor
import asyncio
import pymongo

# ✅ MongoDB Connection (Database me User Data Store karne ke liye)
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

# ✅ Initialize bots & dispatchers lists
bots = []
dispatchers = []

# ✅ Start Command Handler (User Database me Save hoga)
async def start_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    bot_username = (await bot.get_me()).username

    # ✅ Check if user already exists
    user_data = users_collection.find_one({"user_id": user_id, "bot_username": bot_username})
    if not user_data:
        users_collection.insert_one({"user_id": user_id, "bot_username": bot_username})
        await message.reply(f"👋 Hello {message.from_user.first_name}, Welcome to {bot_username}!")
    else:
        await message.reply(f"✅ You are already registered in {bot_username}!")

# ✅ Broadcast Message to All Users
async def broadcast_handler(message: types.Message):
    if message.from_user.id not in [123456789]:  # ✅ Admin User ID (Change karo)
        return await message.reply("🚫 You are not authorized to use this command!")

    text = message.text.replace("/broadcast ", "")
    sent_count = 0

    # ✅ Sabhi Bots ke Users ko Message bhejne ka process
    for bot in bots:
        bot_username = (await bot.get_me()).username
        users = users_collection.find({"bot_username": bot_username})
        
        for user in users:
            try:
                await bot.send_message(user["user_id"], text)
                sent_count += 1
            except:
                pass  # ✅ Agar koi user bot block kar de to ignore karenge
    
    await message.reply(f"✅ Broadcast sent to {sent_count} users.")

# ✅ Function to register bots
def register_multi_bot_handlers():
    for token in bot_tokens:
        bot = Bot(token=token)
        dp = Dispatcher(bot)

        # ✅ Register Commands
        dp.register_message_handler(lambda message: start_handler(message, bot), commands=['start'])
        dp.register_message_handler(broadcast_handler, commands=['broadcast'])
        
        bots.append(bot)
        dispatchers.append(dp)

# ✅ Function to start all bots
async def start_multi_bots():
    await asyncio.gather(*(dp.start_polling() for dp in dispatchers))

# ✅ Run the bot system
if __name__ == "__main__":
    register_multi_bot_handlers()
    executor.start(start_multi_bots())
