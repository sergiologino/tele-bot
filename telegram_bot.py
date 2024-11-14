import logging
import datetime
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Список вопросов и пользователей
QUESTIONS = ["Вопрос 1", "Вопрос 2", "Вопрос 3"]
# Словарь пользователей с временем опроса. Формат: {user_id: "HH:MM"}
USER_SCHEDULE = {
    1833578140: "09:00",# Сергей
    109518209: "10:30",  # Андрей
    1968367418: "10:00", # Иван
    481451826: "10:00"  # Майя
}

OWNER_ID = 428540866  # Ваш Telegram ID как владельца бота

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionBot:
    def __init__(self):
        self.user_state = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if user_id in USER_SCHEDULE:
            await context.bot.send_message(chat_id=user_id, text="Добро пожаловать! Я буду задавать вам вопросы каждый рабочий день.")
        else:
            await context.bot.send_message(chat_id=user_id, text="Извините, вы не включены в список участников.")

    async def ask_questions_for_user(self, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        self.user_state[user_id] = {"question_index": 0, "answers": []}
        await context.bot.send_message(chat_id=user_id, text=QUESTIONS[0])

    async def handle_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if user_id not in self.user_state:
            return

        user_data = self.user_state[user_id]
        user_data["answers"].append(update.message.text)
        user_data["question_index"] += 1

        if user_data["question_index"] < len(QUESTIONS):
            next_question = QUESTIONS[user_data["question_index"]]
            await context.bot.send_message(chat_id=user_id, text=next_question)
        else:
            answers_text = "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(user_data["answers"])])
            await context.bot.send_message(chat_id=OWNER_ID, text=f"Ответы пользователя {user_id}:\n{answers_text}")
            del self.user_state[user_id]

    def setup_scheduled_task(self, application: Application) -> None:
        scheduler = AsyncIOScheduler()
        for user_id, time in USER_SCHEDULE.items():
            hour, minute = map(int, time.split(":"))
            scheduler.add_job(self.ask_questions_for_user, CronTrigger(day_of_week="mon-fri", hour=hour, minute=minute), args=[application, user_id])
        scheduler.start()

# Создаем объект бота
question_bot = QuestionBot()

# Настраиваем бота
def main() -> None:
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Обработчики
    application.add_handler(CommandHandler("start", question_bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, question_bot.handle_response))

    # Настраиваем планировщик для отправки вопросов каждый рабочий день в 9 утра
    question_bot.setup_scheduled_task(application)

    application.run_polling()

if __name__ == "__main__":
    main()
