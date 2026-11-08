
import os
import json
import logging
import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    ContentType,
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


# =====================================
# НАСТРОЙКИ
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН_БОТА")

# ТВОЯ ССЫЛКА GITHUB PAGES
WEBAPP_URL = "https://i8103719-ship-it.github.io/clicker-game/"

# Telegram ID администратора
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))


# =====================================
# СОЗДАНИЕ БОТА
# =====================================

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()
router = Router()

dp.include_router(router)


# =====================================
# КОМАНДА /START
# =====================================

@router.message(CommandStart())
async def start_handler(message: Message):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть Кликер",
                    web_app=WebAppInfo(
                        url=WEBAPP_URL
                    )
                )
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

    await message.answer(
        "<b>Добро пожаловать в Кликер!</b>\n\n"
        "Нажимай на монету и зарабатывай очки.\n"
        "Твой прогресс сохраняется автоматически.\n\n"
        "Нажми кнопку ниже, чтобы начать игру.",
        reply_markup=keyboard
    )


# =====================================
# ПОЛУЧЕНИЕ РЕЗУЛЬТАТА ИЗ MINI APP
# =====================================

@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def web_app_data_handler(message: Message):

    try:
        raw_data = message.web_app_data.data

        data = json.loads(raw_data)

        score = data.get("score")

        # Проверка результата
        if isinstance(score, bool) or not isinstance(score, int):
            await message.answer(
                "Ошибка: некорректный результат."
            )
            return

        if score < 0 or score > 10**15:
            await message.answer(
                "Ошибка: недопустимый результат."
            )
            return

        user = message.from_user

        username = (
            f"@{user.username}"
            if user.username
            else "Не указан"
        )

        # Сообщение игроку
        await message.answer(
            f"<b>Твой результат: {score:,} очков!</b>".replace(",", " ")
        )

        # Сообщение администратору
        if ADMIN_ID:

            admin_text = (
                "<b>Новый результат игрока</b>\n\n"
                f"Имя: {user.full_name}\n"
                f"Username: {username}\n"
                f"ID: <code>{user.id}</code>\n\n"
                f"<b>Результат: {score:,} очков</b>"
            ).replace(",", " ")

            try:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_text
                )

            except Exception:
                logging.exception(
                    "Не удалось отправить результат администратору"
                )

    except (json.JSONDecodeError, TypeError, ValueError):
        await message.answer(
            "Не удалось обработать результат."
        )

    except Exception:
        logging.exception("Ошибка обработки результата")

        await message.answer(
            "Произошла ошибка."
        )


# =====================================
# ЗАПУСК
# =====================================

async def main():

    logging.info("Кликер запущен!")

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
  
