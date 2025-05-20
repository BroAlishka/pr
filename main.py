
#"8195308262:AAFuWetZ6_tfEZsR_pGdsn6NjJa7KDjRToU"

import logging
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- Настройки ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8195308262:AAFuWetZ6_tfEZsR_pGdsn6NjJa7KDjRToU"  # Замените на реальный токен!

# --- Данные викторины ---
QUIZ_DATA = [
    {"question": "Кто был первым царём России?", "answer": "Иван Грозный"},
    {"question": "В каком году произошло Крещение Руси?", "answer": "988"},
    {"question": "Кто победил в Ледовом побоище?", "answer": "Александр Невский"},
    {"question": "Как называлась первая русская летопись?", "answer": "Повесть временных лет"},
    {"question": "Кто основал Санкт-Петербург?", "answer": "Пётр I"},
    {"question": "В каком году началась Великая Отечественная война?", "answer": "1941"},
    {"question": "Как звали первого космонавта?", "answer": "Юрий Гагарин"},
]

# --- Глобальные переменные ---
current_question = None
correct_answer = None
user_scores = {}
used_questions = set()

# --- Инициализация бота ---
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="/quiz"))
    await message.answer(
        "📜 Привет! Я бот-викторина по истории России.\n"
        "Нажми /quiz в группе, чтобы начать игру!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# --- Команда /quiz ---
@dp.message(Command("quiz"), lambda msg: msg.chat.type in ["group", "supergroup"])
async def cmd_quiz(message: types.Message):
    global current_question, correct_answer, used_questions
    
    # Выбираем неиспользованный вопрос
    available_questions = [q for q in QUIZ_DATA if q["question"] not in used_questions]
    if not available_questions:
        await message.answer("Все вопросы закончились! Начните заново.")
        used_questions.clear()
        return
    
    question_data = random.choice(available_questions)
    current_question = question_data["question"]
    correct_answer = question_data["answer"].lower()
    used_questions.add(current_question)
    
    await message.answer(f"❓ Вопрос: {current_question}")

# --- Проверка ответов ---
@dp.message(lambda msg: msg.chat.type in ["group", "supergroup"])
async def check_answer(message: types.Message):
    global current_question, correct_answer
    
    if not current_question:
        return
    
    user_answer = message.text.strip().lower()
    user_id = message.from_user.id
    
    if user_answer == correct_answer:
        user_scores[user_id] = user_scores.get(user_id, 0) + 1
        await message.reply(
            f"✅ {message.from_user.first_name}, правильно! +1 балл.\n"
            f"Твой счёт: {user_scores[user_id]}"
        )
    else:
        await message.reply(
            f"❌ Неверно! Правильный ответ: {correct_answer.capitalize()}"
        )
    
    current_question = None  # Сбрасываем вопрос после ответа

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())