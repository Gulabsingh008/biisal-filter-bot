from pyrogram import Client, filters
from database.users_chats_db import Database
from database.ia_filterdb import Media
import random

# Database instance
db = Database()

@Client.on_message(filters.command("today"))
async def today_handler(client, message):
    user_id = message.from_user.id
    user_data = await db.users.find_one({"id": user_id})
    
    if not user_data:
        await message.reply("आप रजिस्टर नहीं हैं! पहले /start दबाएँ।")
        return
    
    is_premium = user_data.get("is_premium", False)
    daily_limit = user_data.get("daily_limit", 0)
    max_limit = 15 if is_premium else 3  # प्रीमियम = 15 फाइल, फ्री = 3 फाइल
    
    if daily_limit >= max_limit:
        await message.reply("⚠️ आज की लिमिट समाप्त हो गई है! कृपया कल पुनः प्रयास करें।")
        return
    
    # रैंडम फाइल चुनना
    total_files = await Media.count_documents({})
    if total_files == 0:
        await message.reply("कोई फाइल उपलब्ध नहीं है!")
        return
    
    random_index = random.randint(0, total_files - 1)
    random_file = await Media.find().skip(random_index).limit(1).to_list(1)
    
    if not random_file:
        await message.reply("कोई फाइल नहीं मिली!")
        return
    
    # फाइल भेजना
    file_data = random_file[0]
    await message.reply_document(document=file_data["file_id"], caption=file_data.get("caption", "Here is your file!"))
    
    # लिमिट अपडेट करना
    await db.users.update_one({"id": user_id}, {"$inc": {"daily_limit": 1}})
    
