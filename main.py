import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (лучше хранить в .env)
TOKEN = "8195308262:AAFuWetZ6_tfEZsR_pGdsn6NjJa7KDjRToU"

# Инициализация бота
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Данные викторины
quiz_data = [
    {"question": "Кто основал Санкт-Петербург?", "answer": "Пётр I"},
    {"question": "В каком году была Куликовская битва?", "answer": "1380"},
    {"question": "Первый царь из династии Романовых?", "answer": "Михаил Фёдорович"}
]
current_question = None
user_scores = {}

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="/quiz"))
    await message.answer(
        "📜 Привет! Я бот-викторина по истории России.\nНажми /quiz чтобы начать!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Команда /quiz
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    global current_question
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("Эта команда работает только в группах!")
        return
    
    question = quiz_data[len(user_scores) % len(quiz_data)]
    current_question = question["question"]
    await message.answer(f"❓ Вопрос: {current_question}\n(Ответ: {question['answer']})")

# Обработка ответов
@dp.message()
async def check_answer(message: types.Message):
    global current_question
    if not current_question or message.chat.type not in ("group", "supergroup"):
        return
    
    user_id = message.from_user.id
    correct_answer = quiz_data[len(user_scores) % len(quiz_data)]["answer"]
    
    if message.text.strip().lower() == correct_answer.lower():
        user_scores[user_id] = user_scores.get(user_id, 0) + 1
        await message.reply(
            f"✅ {message.from_user.first_name}, верно! Твой счёт: {user_scores[user_id]}\n"
            f"Следующий вопрос: /quiz"
        )
        current_question = None

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())