import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Вставь сюда свой токен от BotFather
BOT_TOKEN = "8097565475:AAE4qktwIlrZ19rJbJEr4NLIV970GPxKd3A"

def is_part_number_like(text: str) -> bool:
    """Проверяет, похоже ли слово на артикул (P/N)."""
    return bool(re.match(r"^[A-Z0-9\-]+,?$", text, re.IGNORECASE)) and any(char.isdigit() for char in text)

def parse_parts(text: str) -> str:
    lines = text.strip().splitlines()
    result_lines = ["Hello Team, \n\nCould you please provide us with a quotation for the following part:\n"]

    for line in lines:
        if not line.strip():
            continue

        parts = re.split(r"\s+", line.strip())
        if len(parts) < 3:
            result_lines.append(f"⚠️ Не удалось разобрать строку: {line}\n")
            continue

        pn = parts[0]                  # Основной номер
        qty = parts[-1]                # Количество
        alt_list = []
        index = 1

        # Собираем альтернативы, пока похоже на артикулы
        while index < len(parts) - 2 and is_part_number_like(parts[index]):
            alt_list.append(parts[index].rstrip(","))
            index += 1

        # Описание — всё между альтернативами и qty
        description = " ".join(parts[index:-1])

        # Сбор результата
        result_lines.append(f"P/N: {pn}")
        result_lines.append(f"Description: {description}")
        result_lines.append(f"Qty: {qty} EA")
        if alt_list:
            result_lines.append(f"Alt: {', '.join(alt_list)}")
        result_lines.append("")  # Пустая строка между позициями

    result_lines.append("")
    
    return "\n".join(result_lines)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь список позиций в формате:\n\n"
        "P/N [Alt1, Alt2, ...] Description Qty\n\n"
        "Пример:\n"
        "FG797-01-0800  852-28R08, 8525-30, EC12  CAP,CONNECTOR  1"
    )

# Обработка текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    formatted = parse_parts(user_text)
    await update.message.reply_text('Request for Quotation:')
    await update.message.reply_text(formatted)

# Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
