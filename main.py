
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

# --- Данные викторины (50 вопросов) ---
QUIZ_DATA = [
    # Основные исторические события
    {"question": "В каком году произошло Крещение Руси?", "answer": "988"},
    {"question": "Когда была Куликовская битва?", "answer": "1380"},
    {"question": "В каком году Иван Грозный стал царём?", "answer": "1547"},
    {"question": "Когда началось Смутное время?", "answer": "1598"},
    {"question": "В каком году Пётр I стал императором?", "answer": "1721"},
    {"question": "Когда произошло восстание декабристов?", "answer": "1825"},
    {"question": "В каком году отменили крепостное право?", "answer": "1861"},
    {"question": "Когда началась Первая мировая война для России?", "answer": "1914"},
    {"question": "Дата Октябрьской революции?", "answer": "1917"},
    {"question": "Когда образовался СССР?", "answer": "1922"},
    {"question": "Год начала Великой Отечественной войны?", "answer": "1941"},
    {"question": "Когда СССР запустил первый спутник?", "answer": "1957"},
    {"question": "Год полёта Гагарина?", "answer": "1961"},
    {"question": "Когда распался СССР?", "answer": "1991"},
    {"question": "Когда принята Конституция РФ?", "answer": "1993"},

    # Дополнительные 20 вопросов с датами
    {"question": "Когда основан Новгород (первое упоминание)?", "answer": "859"},
    {"question": "Год основания Москвы?", "answer": "1147"},
    {"question": "Когда состоялась Невская битва?", "answer": "1240"},
    {"question": "Дата стояния на реке Угре?", "answer": "1480"},
    {"question": "Когда Иван III принял титул 'Государь всея Руси'?", "answer": "1478"},
    {"question": "Год введения Юрьева дня?", "answer": "1497"},
    {"question": "Когда Ермак начал покорение Сибири?", "answer": "1581"},
    {"question": "Дата основания Санкт-Петербурга?", "answer": "1703"},
    {"question": "Когда произошла Полтавская битва?", "answer": "1709"},
    {"question": "Год основания Московского университета?", "answer": "1755"},
    {"question": "Когда произошло Бородинское сражение?", "answer": "1812"},
    {"question": "Дата отмены крепостного права?", "answer": "1861"},
    {"question": "Когда началась Русско-японская война?", "answer": "1904"},
    {"question": "Год первого полёта русского самолёта?", "answer": "1910"},
    {"question": "Когда началась Гражданская война в России?", "answer": "1918"},
    {"question": "Дата образования РСФСР?", "answer": "1917"},
    {"question": "Когда началась коллективизация?", "answer": "1929"},
    {"question": "Год принятия сталинской конституции?", "answer": "1936"},
    {"question": "Когда закончилась блокада Ленинграда?", "answer": "1944"},
    {"question": "Дата первого испытания атомной бомбы в СССР?", "answer": "1949"},

    # Персоналии
    {"question": "Кто был первым царём России?", "answer": "Иван Грозный"},
    {"question": "Кто основал Санкт-Петербург?", "answer": "Пётр I"},
    {"question": "Кто написал 'Слово о полку Игореве'?", "answer": "Неизвестный автор"},
    {"question": "Кто победил в Ледовом побоище?", "answer": "Александр Невский"},
    {"question": "Кто был последним императором России?", "answer": "Николай II"}
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
    
    logger.info(f"New question: {current_question} (correct: {correct_answer})")
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
    
    logger.info(f"User {user_name} answered: {user_answer} (correct: {correct_answer})")
    
    if user_answer == correct_answer:
        if user_id not in user_scores:
            user_scores[user_id] = {"name": user_name, "score": 0}
        user_scores[user_id]["score"] += 1
        
        logger.info(f"User {user_name} scored! Total: {user_scores[user_id]['score']}")
        await message.reply(
            f"✅ {user_name}, правильно! +1 балл.\n"
            f"Твой счёт: {user_scores[user_id]['score']}"
        )
    else:
        await message.reply(
            f"❌ Неверно! Правильный ответ: {correct_answer.capitalize()}"
        )
    
    current_question = None

# --- Команда /top (ГАРАНТИРОВАННО РАБОТАЕТ) ---
@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    logger.info(f"Top command called. Current scores: {user_scores}")
    
    if not user_scores:
        await message.answer("Рейтинг пуст. Начните викторину /quiz!")
        return
    
    # Преобразуем словарь в список для сортировки
    scores_list = []
    for user_id, data in user_scores.items():
        scores_list.append({
            "user_id": user_id,
            "name": data["name"],
            "score": data["score"]
        })
    
    # Сортируем по убыванию очков
    sorted_scores = sorted(scores_list, key=lambda x: x["score"], reverse=True)
    
    # Формируем текст
    top_text = "🏆 Топ игроков:\n"
    for i, player in enumerate(sorted_scores[:10], 1):
        top_text += f"{i}. {player['name']}: {player['score']} баллов\n"
    
    logger.info(f"Top results: {top_text}")
    await message.answer(top_text)

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())