import logging
from aiogram import Bot, Dispatcher, executor, types

# Logging sozlamasi
logging.basicConfig(level=logging.INFO)

# --- SOZLAMALAR ---
TOKEN = "9122487573:AAGj0O9zjU5FUeI3y7as7-EoE86_fWNr1RY"
CHANNEL_ID = "@kinolar_tarjimatv"  # Majburiy obuna kanali
ADMIN_ID = 6976504734  # Sizning Telegram ID raqamingiz

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Kino bazasi (Kino kodlari va maxfiy kanaldagi post havolalari)
MOVIES = {
    "101": "https://t.me/c/2473955509/15",
    "102": "https://t.me/c/2473955509/20",
}


# Obunani tekshirish funksiyasi
async def check_sub_channel(user_id):
  try:
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if member.status in ["member", "administrator", "creator", "restricted"]:
      return True
  except Exception:
    pass
  return False


# /start komandasi
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
  user_id = message.from_user.id

  if CHANNEL_ID and not await check_sub_channel(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Kanalga obuna bo'lish / Zayavka tashlash",
            url=f"https://t.me/{CHANNEL_ID.lstrip('@')}",
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            "🔄 Obunani tekshirish", callback_data="check_subscription"
        )
    )

    await message.answer(
        "👋 Assalomu alaykum! Kino va videolarni olish uchun avval quyidagi"
        " kanalimizga obuna bo'ling (yoki zayavka yuboring):\n\nKanalga kirib"
        " 'Obuna bo'lish' tugmasini bosgach, pastdagi **'Obunani tekshirish'**"
        " tugmasini bosing:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return

  await message.answer(
      "✅ Obunangiz tasdiqlandi!\n\nEndi menga kino kodini yuboring, men sizga"
      " kinoni tashlab beraman."
  )


# Obunani tekshirish tugmasi bosilganda
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_callback_sub(callback_query: types.CallbackQuery):
  user_id = callback_query.from_user.id
  if await check_sub_channel(user_id):
    await bot.answer_callback_query(
        callback_query.id, text="Rahmat, obuna tasdiqlandi!"
    )
    await bot.send_message(
        user_id,
        "✅ Tabriklayman! Endi kino kodini yuborishingiz mumkin:",
    )
    try:
      await bot.delete_message(
          callback_query.message.chat.id, callback_query.message.message_id
      )
    except:
      pass
  else:
    await bot.answer_callback_query(
        callback_query.id,
        text="Siz hali kanalga obuna bo'lmadingiz yoki zayavka tashlamadingiz!",
        show_alert=True,
    )


# Kodlar bo'yicha kinolarni topib berish
@dp.message_handler()
async def get_movie(message: types.Message):
  user_id = message.from_user.id

  if CHANNEL_ID and not await check_sub_channel(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Kanalga obuna bo'lish",
            url=f"https://t.me/{CHANNEL_ID.lstrip('@')}",
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            "🔄 Obunani tekshirish", callback_data="check_subscription"
        )
    )
    await message.answer(
        "⚠️ Kinoni olish uchun avval kanalimizga obuna bo'lishingiz kerak!",
        reply_markup=keyboard,
    )
    return

  code = message.text.strip()

  if code in MOVIES:
    movie_link = MOVIES[code]
    await message.answer(
        f"🎬 Marhamat, siz so'ragan kino:\n{movie_link}"
    )
  else:
    await message.answer(
        "❌ Bunday kodli kino topilmadi. To'g'ri kodni kiriting:"
    )


if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
