import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import database

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для заметок.\n\n"
        "Команды:\n"
        "/save <текст> — сохранить заметку\n"
        "/show — показать все мои заметки\n"
        "/delete N — удалить заметку с номером N"
    )


async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите текст заметки: /save <текст>")
        return
    text = " ".join(context.args)
    database.save_note(update.effective_user.id, text)
    await update.message.reply_text("Заметка сохранена.")


async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = database.get_notes(update.effective_user.id)
    if not notes:
        await update.message.reply_text("У вас пока нет заметок.")
        return
    lines = []
    for i, (_, text, created_at) in enumerate(notes, start=1):
        date = created_at[:10].replace("-", ".")
        # Convert YYYY.MM.DD → DD.MM.YYYY
        parts = date.split(".")
        formatted_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
        lines.append(f"{i}. [{formatted_date}] {text}")
    await update.message.reply_text("Ваши заметки:\n" + "\n".join(lines))


async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите номер заметки: /delete N")
        return
    try:
        position = int(context.args[0])
        if position < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Номер заметки должен быть положительным числом.")
        return

    deleted = database.delete_note(update.effective_user.id, position)
    if deleted:
        await update.message.reply_text(f"Заметка №{position} удалена.")
    else:
        await update.message.reply_text("Заметка не найдена.")


def main():
    database.init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("save", save_note))
    app.add_handler(CommandHandler("show", show_notes))
    app.add_handler(CommandHandler("delete", delete_note))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
