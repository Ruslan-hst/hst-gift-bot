import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BITRIX_WEBHOOK = os.environ.get("BITRIX_WEBHOOK")


def create_bitrix_deal(name: str, telegram_id: int, username: str) -> int | None:
    url = BITRIX_WEBHOOK + "crm.deal.add.json"
    data = {
        "fields[TITLE]": f"Telegram: {name}",
        "fields[SOURCE_ID]": "WEB",
        "fields[COMMENTS]": f"Telegram ID: {telegram_id}\nUsername: @{username}\nИсточник: Telegram бот @hst_gift_bot",
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        result = r.json()
        return result.get("result")
    except Exception as e:
        logging.error(f"Битрикс ошибка: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.full_name or "Без имени"
    username = user.username or "нет"

    deal_id = create_bitrix_deal(name, user.id, username)

    if deal_id:
        await update.message.reply_text(
            f"Привет, {name}! 👋\n\nТы записан, менеджер скоро свяжется."
        )
        logging.info(f"Сделка создана: {deal_id} для {name}")
    else:
        await update.message.reply_text(
            "Привет! Напиши нам, поможем подобрать клюшку. 🏒"
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
