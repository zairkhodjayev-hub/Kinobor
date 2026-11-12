import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Token va sozlamalar
TOKEN = "9122487573:AAGj0O9zjU5FUeI3y7as7-EoE86_fWNr1RY"
ADMIN_ID = 6976504734  # Sizning admin ID raqamingiz

# Vaqtinchalik baza (Kino kodlari va majburiy kanallar)
MOVIES = {
    "101": "https://t.me/c/2473955509/15",
    "102": "https://t.me/c/2473955509/20",
}
CHANNELS = ["@kinolar_tarjimatv"]  # Majburiy obuna kanallari
USERS = set()  # Botdan foydalanuvchilar

dp = Dispatcher(storage=MemoryStorage())

# FSM Holatlar (Admin amallari uchun)
class AdminStates(StatesGroup):
    waiting_for_movie_code = State()
    waiting_for_movie_link = State()
    waiting_for_del_code = State()
    waiting_for_broadcast = State()
    waiting_for_add_channel = State()
    waiting_for_del_channel = State()

# Obunani tekshirish funksiyasi
async def check_sub_channel(bot: Bot, user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator", "restricted"]:
                return False
        except Exception:
            return False
    return True

# Admin klaviaturasi (Pastdagi tugmalar)
def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Foydalanuvchilarga xabar jo'natish")],
            [KeyboardButton(text="➕ Majburiy obuna kanal qo'shish"), KeyboardButton(text="❌ Majburiy obuna kanal o'chirish")],
            [KeyboardButton(text="🎬 Film qo'shish"), KeyboardButton(text="🗑 Film o'chirish")],
            [KeyboardButton(text="📄 Malumotlar filesini yuklash")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    USERS.add(user_id)

    # Agar foydalanuvchi admin bo'lsa
    if user_id == ADMIN_ID:
        await message.answer(
            "👨‍💻 Siz adminsiz! O'z huquqlaringizdan foydalaning! 🎬",
            reply_markup=get_admin_keyboard()
        )
        return

    # Oddiy foydalanuvchi uchun majburiy obunani tekshirish
    if CHANNELS and not await check_sub_channel(bot, user_id):
        buttons = []
        for ch in CHANNELS:
            buttons.append([InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{ch.lstrip('@')}")])
        buttons.append([InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data="check_subscription")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            "👋 Assalomu alaykum! Kino va videolarni olish uchun avval quyidagi kanalimizga obuna bo'ling, so'ng 'Obunani tekshirish' tugmasini bosing:",
            reply_markup=keyboard
        )
        return

    await message.answer("✅ Obunangiz tasdiqlandi!\n\nEndi menga kino kodini yuboring.")

@dp.callback_query(F.data == "check_subscription")
async def process_callback_sub(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if await check_sub_channel(bot, user_id):
        await callback.answer("Rahmat, obuna tasdiqlandi!", show_alert=False)
        await bot.send_message(user_id, "✅ Tabriklayman! Endi kino kodini yuborishingiz mumkin:")
        try:
            await callback.message.delete()
        except:
            pass
    else:
        await callback.answer("Siz hali hamma kanalga obuna bo'lmadingiz!", show_alert=True)

# --- ADMIN PANEL BOSHQARUVI ---

@dp.message(F.text == "🎬 Film qo'shish")
async def add_movie_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_movie_code)
    await message.answer("🎬 Yangi kino uchun kod kiriting (masalan: 103):")

@dp.message(AdminStates.waiting_for_movie_code)
async def process_movie_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text.strip())
    await state.set_state(AdminStates.waiting_for_movie_link)
    await message.answer("🔗 Endi kino havolasini (video ssilkasi yoki file_id) yuboring:")

@dp.message(AdminStates.waiting_for_movie_link)
async def process_movie_link(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("code")
    link = message.text.strip()
    MOVIES[code] = link
    await state.clear()
    await message.answer(f"✅ Kino muvaffaqiyatli qo'shildi!\nKod: {code}", reply_markup=get_admin_keyboard())

@dp.message(F.text == "🗑 Film o'chirish")
async def del_movie_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_del_code)
    await message.answer(f"Mavjud kinolar kodlari:\n{list(MOVIES.keys())}\n\nO'chirmoqchi bo'lgan kino kodini kiriting:")

@dp.message(AdminStates.waiting_for_del_code)
async def process_del_movie(message: Message, state: FSMContext):
    code = message.text.strip()
    if code in MOVIES:
        del MOVIES[code]
        await message.answer(f"✅ {code}-kodli kino o'chirildi!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.", reply_markup=get_admin_keyboard())
    await state.clear()

@dp.message(F.text == "➕ Majburiy obuna kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_add_channel)
    await message.answer("Kanal usernamini yuboring (masalan: @kanal_nomi):")

@dp.message(AdminStates.waiting_for_add_channel)
async def process_add_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    if channel not in CHANNELS:
        CHANNELS.append(channel)
        await message.answer(f"✅ {channel} majburiy obunaga qo'shildi!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("⚠️ Bu kanal allaqachon ro'yxatda bor.", reply_markup=get_admin_keyboard())
    await state.clear()

@dp.message(F.text == "❌ Majburiy obuna kanal o'chirish")
async def del_channel_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_del_channel)
    await message.answer(f"Hozirgi kanallar:\n{CHANNELS}\n\nO'chirmoqchi bo'lgan kanalni yuboring:")

@dp.message(AdminStates.waiting_for_del_channel)
async def process_del_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    if channel in CHANNELS:
        CHANNELS.remove(channel)
        await message.answer(f"✅ {channel} olib tashlandi!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ Bunday kanal topilmadi.", reply_markup=get_admin_keyboard())
    await state.clear()

@dp.message(F.text == "📢 Foydalanuvchilarga xabar jo'natish")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_broadcast)
    await message.answer("Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni (matn, rasm yoki video) yuboring:")

@dp.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    count = 0
    for user_id in USERS:
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ Xabar {count} ta foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=get_admin_keyboard())

@dp.message(F.text == "📄 Malumotlar filesini yuklash")
async def send_stats(message: Message):
    if message.from_user.id != ADMIN_ID: return
    stats_text = f"Bot statistikasi:\nFoydalanuvchilar soni: {len(USERS)}\nKinolar soni: {len(MOVIES)}\nKanallar: {CHANNELS}"
    await message.answer(stats_text, reply_markup=get_admin_keyboard())

# Oddiy foydalanuvchilar kino kodi yuborganda
@dp.message()
async def get_movie(message: Message, bot: Bot):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return  # Admin panel tugmalarini bosganda bu yerga kirmasligi uchun

    if CHANNELS and not await check_sub_channel(bot, user_id):
        buttons = []
        for ch in CHANNELS:
            buttons.append([InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{ch.lstrip('@')}")])
        buttons.append([InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data="check_subscription")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("⚠️ Kinoni olish uchun avval kanalimizga obuna bo'lishingiz kerak!", reply_markup=keyboard)
        return

    code = message.text.strip()
    if code in MOVIES:
        await message.answer(f"🎬 Marhamat, siz so'ragan kino:\n{MOVIES[code]}")
    else:
        await message.answer("❌ Bunday kodli kino topilmadi. To'g'ri kodni kiriting:")

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
