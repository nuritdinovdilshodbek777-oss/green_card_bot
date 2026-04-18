import logging
from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = "8648243685:AAH_hlO_6qzje46KyPZpB6n5iYP33rKEquM"
ADMIN_ID = 6918216299

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_step = {}
users_data = {}
user_requests = {}

# INFO TEXTS
texts = [
"""🟢 GREEN CARD NIMA O‘ZI?

Green Card — bu AQSHda doimiy yashash va ishlash huquqini beradigan hujjat.

Oddiy qilib aytganda:
• AQSHda qonuniy yashaysiz
• Ishlash huquqi bor
• O‘qish mumkin
• Keyinchalik fuqarolik olish mumkin

Lekin bu fuqarolik emas!""",

"""2️⃣ GREEN CARD QANDAY OLINADI?

Eng mashhur yo‘l — DV Lottery

• AQSH har yili lotereya o‘tkazadi
• Dunyo bo‘yicha odamlar qatnashadi
• Tasodifiy g‘oliblar tanlanadi""",

"""3️⃣ ARIZA QANDAY TOPSHIRILADI?

👉 dvprogram.state.gov

• Ism, familiya
• Tug‘ilgan sana
• Davlat
• Jins
• Rasm
• Oilaviy holat""",

"""4️⃣ RASM TALABLARI:

• Oq fon
• Yuz to‘liq ko‘rinishi
• 6 oy ichida tushgan""",

"""5️⃣ MUHIM QOIDALAR:

• Ariza BEPUL
• 1 marta topshirish
• 2 marta = diskvalifikatsiya
• Natija bir necha oyda chiqadi"""
]

# START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("❓ Ma’lumotim yo‘q", "✅ Hammasini bilaman")
    await message.answer("Assalomu alaykum! Tanlang:", reply_markup=kb)

# INFO BOSHLASH
@dp.message_handler(lambda m: m.text == "❓ Ma’lumotim yo‘q")
async def start_info(message: types.Message):
    user_step[message.from_user.id] = 0
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏭ Tushundim, keyingisi")
    await message.answer(texts[0], reply_markup=kb)

# INFO NEXT
@dp.message_handler(lambda m: m.text == "⏭ Tushundim, keyingisi")
async def next_info(message: types.Message):
    step = user_step.get(message.from_user.id, 0) + 1
    user_step[message.from_user.id] = step

    if step < len(texts):
        await message.answer(texts[step])
    else:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🚀 Xizmatdan foydalanish")
        await message.answer("✅ Barcha ma’lumot tugadi!", reply_markup=kb)

# SERVICE
@dp.message_handler(lambda m: m.text in ["🚀 Xizmatdan foydalanish", "✅ Hammasini bilaman"])
async def service(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👤 1 kishi", "👨‍👩‍👧 Oila")
    await message.answer("Xizmat turini tanlang:", reply_markup=kb)

# 1 KISHI
@dp.message_handler(lambda m: m.text == "👤 1 kishi")
async def one_user(message: types.Message):
    users_data[message.from_user.id] = {
        "count": 1,
        "current": 1,
        "data": []
    }
    await message.answer("1-kishi ma’lumotini kiriting:\nIsm Familiya, Yoshi, Telefon")

# OILA
@dp.message_handler(lambda m: m.text == "👨‍👩‍👧 Oila")
async def family(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(2, 11):
        kb.add(f"{i} kishi")
    await message.answer("Necha kishi?", reply_markup=kb)

# OILA SONI
@dp.message_handler(lambda m: "kishi" in m.text)
async def choose_count(message: types.Message):
    count = int(message.text.split()[0])
    users_data[message.from_user.id] = {
        "count": count,
        "current": 1,
        "data": []
    }
    await message.answer("1-kishi ma’lumotini kiriting:")

# DATA COLLECT
@dp.message_handler()
async def collect_data(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Iltimos tugmalardan foydalaning.")
        return

    data = users_data[user_id]
    data["data"].append(message.text)

    if data["current"] < data["count"]:
        data["current"] += 1
        await message.answer(f"{data['current']}-kishi ma’lumotini kiriting:")
    else:
        user = message.from_user

        text = "🟢 YANGI ARIZA:\n\n"
        text += f"👤 User: {user.full_name}\n"
        text += f"🆔 ID: {user.id}\n"
        text += f"📛 Username: @{user.username}\n\n"
        for i, person in enumerate(data["data"], start=1):
            text += f"{i}-kishi: {person}\n"

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("✅ APPROVE", callback_data=f"ok_{user.id}"),
            types.InlineKeyboardButton("❌ REJECT", callback_data=f"no_{user.id}")
        )

        user_requests[user.id] = data

        await bot.send_message(ADMIN_ID, text, reply_markup=kb)

        await message.answer("✅ Arizangiz yuborildi!")
        del users_data[user_id]

# ADMIN CALLBACK
@dp.callback_query_handler(lambda c: True)
async def process(callback: types.CallbackQuery):
    data = callback.data

    if data.startswith("ok_"):
        user_id = int(data.split("_")[1])
        await bot.send_message(user_id, "✅ Arizangiz qabul qilindi!")
        await callback.message.answer("Approved ✔")

    elif data.startswith("no_"):
        user_id = int(data.split("_")[1])
        await bot.send_message(user_id, "❌ Arizangiz rad etildi.")
        await callback.message.answer("Rejected ❌")

    await callback.answer()

# RUN
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)