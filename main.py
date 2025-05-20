
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

# --- Данные викторины (30 вопросов) ---
QUIZ_DATA = [
    # Первые 20 вопросов (из предыдущей версии)
    {"question": "Кто был первым царём России?", "answer": "Иван Грозный"},
    {"question": "В каком году произошло Крещение Руси?", "answer": "988"},
    {"question": "Кто победил в Ледовом побоище?", "answer": "Александр Невский"},
    {"question": "Как называлась первая русская летопись?", "answer": "Повесть временных лет"},
    {"question": "Кто основал Санкт-Петербург?", "answer": "Пётр I"},
    {"question": "В каком году началась Великая Отечественная война?", "answer": "1941"},
    {"question": "Как звали первого космонавта?", "answer": "Юрий Гагарин"},
    {"question": "Кто написал 'Слово о полку Игореве'?", "answer": "Неизвестный автор"},
    {"question": "В каком году отменили крепостное право?", "answer": "1861"},
    {"question": "Как называлось государство монголо-татар на Руси?", "answer": "Золотая Орda"},
    {"question": "Кто возглавлял Красную Армию в Гражданскую войну?", "answer": "Лев Троцкий"},
    {"question": "Какой город был первой столицей Древней Руси?", "answer": "Новгород"},
    {"question": "Кто был последним императором России?", "answer": "Николай II"},
    {"question": "В каком году произошла Октябрьская революция?", "answer": "1917"},
    {"question": "Как назывался первый русский университет?", "answer": "Московский университет"},
    {"question": "Кто победил в Куликовской битве?", "answer": "Дмитрий Донской"},
    {"question": "Какой князь принял христианство на Руси?", "answer": "Владимир Красно Солнышко"},
    {"question": "В каком году распался СССР?", "answer": "1991"},
    {"question": "Какой город выдержал 900-дневную блокаду?", "answer": "Ленинград"},
    {"question": "Кто написал 'Войну и мир'?", "answer": "Лев Толстой"},

    # Новые 10 вопросов:
    {"question": "Как называлась первая печатная книга на Руси?", "answer": "Апостол"},
    {"question": "Кто возглавил первое кругосветное путешествие России?", "answer": "Иван Крузенштерн"},
    {"question": "В каком году была основана Москва?", "answer": "1147"},
    {"question": "Какой царь ввёл опричнину?", "answer": "Иван Грозный"},
    {"question": "Кто был первым президентом России?", "answer": "Борис Ельцин"},
    {"question": "Какое сражение стало переломным в Великой Отечественной войне?", "answer": "Сталинградская битва"},
    {"question": "Как назывался мирный договор, завершивший Северную войну?", "answer": "Ништадтский"},
    {"question": "Кто создал первый русский театр?", "answer": "Фёдор Волков"},
    {"question": "В каком году Россия стала империей?", "answer": "1721"},
    {"question": "Какой художник написал 'Богатырей'?", "answer": "Виктор Васнецов"}
]

# --- Глобальные переменные ---
current_question = None
correct_answer = None
user_scores = {}  # {user_id: {"name": str, "score": int}}
used_questions = set()

# --- Инициализация бота ---
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="/quiz"),
        types.KeyboardButton(text="/top")
    )
    await message.answer(
        "📜 Привет! Я бот-викторина по истории России.\n"
        "Нажми /quiz в группе, чтобы начать игру!\n"
        "/top - топ игроков",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# --- Команда /quiz ---
@dp.message(Command("quiz"), lambda msg: msg.chat.type in ["group", "supergroup"])
async def cmd_quiz(message: types.Message):
    global current_question, correct_answer, used_questions
    
    if len(used_questions) >= len(QUIZ_DATA):
        used_questions.clear()
        await message.answer("Все вопросы закончились! Начинаем заново.")
    
    available_questions = [q for q in QUIZ_DATA if q["question"] not in used_questions]
    question_data = random.choice(available_questions)
    
    current_question = question_data["question"]
    correct_answer = question_data["answer"].lower()
    used_questions.add(current_question)
    
    await message.answer(f"❓ Вопрос: {current_question}")

# --- Проверка ответов ---
@dp.message(lambda msg: msg.chat.type in ["group", "supergroup"])
async def check_answer(message: types.Message):
    global current_question, correct_answer
    
    if not current_question or message.text.startswith('/'):
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_answer = message.text.strip().lower()
    
    if user_answer == correct_answer:
        if user_id not in user_scores:
            user_scores[user_id] = {"name": user_name, "score": 0}
        user_scores[user_id]["score"] += 1
        
        await message.reply(
            f"✅ {user_name}, правильно! +1 балл.\n"
            f"Твой счёт: {user_scores[user_id]['score']}"
        )
    else:
        await message.reply(
            f"❌ Неверно! Правильный ответ: {correct_answer.capitalize()}"
        )
    
    current_question = None

# --- Команда /top (ИСПРАВЛЕННАЯ) ---
@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if not user_scores:
        await message.answer("Рейтинг пуст. Начните викторину /quiz!")
        return
    
    # Получаем и сортируем игроков
    sorted_players = sorted(
        user_scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    
    # Формируем текст
    top_text = "🏆 Топ игроков:\n"
    for idx, player in enumerate(sorted_players[:10], 1):
        top_text += f"{idx}. {player['name']}: {player['score']} баллов\n"
    
    await message.answer(top_text)

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())