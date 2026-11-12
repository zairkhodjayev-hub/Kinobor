import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

TOKEN = "9122487573:AAGj0O9zjU5FUeI3y7as7-EoE86_fWNr1RY"
CHANNEL_ID = "@kinolar_tarjimatv"
ADMIN_ID = 6976504734

MOVIES = {
    "101": "https://t.me/c/2473955509/15",
    "102": "https://t.me/c/2473955509/20",
}

dp = Dispatcher()


async def check_sub_channel(bot: Bot, user_id: int) -> bool:
  try:
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if member.status in ["member", "administrator", "creator", "restricted"]:
      return True
  except Exception:
    pass
  return False


@dp.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
  user_id = message.from_user.id

  if CHANNEL_ID and not await check_sub_channel(bot, user_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo'lish",
                    url=f"https://t.me/{CHANNEL_ID.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Obunani tekshirish",
                    callback_data="check_subscription",
                )
            ],
        ]
    )
    await message.answer(
        "👋 Assalomu alaykum! Kino va videolarni olish uchun avval quyidagi"
        " kanalimizga obuna bo'ling, so'ng 'Obunani tekshirish' tugmasini"
        " bosing:",
        reply_markup=keyboard,
    )
    return

  await message.answer(
      "✅ Obunangiz tasdiqlandi!\n\nEndi menga kino kodini yuboring."
  )


@dp.callback_query(F.data == "check_subscription")
async def process_callback_sub(callback: CallbackQuery, bot: Bot):
  user_id = callback.from_user.id
  if await check_sub_channel(bot, user_id):
    await callback.answer("Rahmat, obuna tasdiqlandi!", show_alert=False)
    await bot.send_message(
        user_id, "✅ Tabriklayman! Endi kino kodini yuborishingiz mumkin:"
    )
    try:
      await callback.message.delete()
    except:
      pass
  else:
    await callback.answer(
        "Siz hali kanalga obuna bo'lmadingiz!", show_alert=True
    )


@dp.message()
async def get_movie(message: Message, bot: Bot):
  user_id = message.from_user.id

  if CHANNEL_ID and not await check_sub_channel(bot, user_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo'lish",
                    url=f"https://t.me/{CHANNEL_ID.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Obunani tekshirish",
                    callback_data="check_subscription",
                )
            ],
        ]
    )
    await message.answer(
        "⚠️ Kinoni olish uchun avval kanalimizga obuna bo'lishingiz kerak!",
        reply_markup=keyboard,
    )
    return

  code = message.text.strip()
  if code in MOVIES:
    await message.answer(f"🎬 Marhamat, siz so'ragan kino:\n{MOVIES[code]}")
  else:
    await message.answer(
        "❌ Bunday kodli kino topilmadi. To'g'ri kodni kiriting:"
    )


async def main():
  bot = Bot(token=TOKEN)
  await dp.start_polling(bot)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, stream=sys.stdout)
  asyncio.run(main())
