import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 6803356420  # your Telegram user ID

# project_key -> saved_message_id
FILE_MAP = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if args:
        key = args[0]
        if key in FILE_MAP:
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=ADMIN_ID,  # Saved Messages is your own chat
                message_id=FILE_MAP[key],
                caption=(
                    "🎉 Here’s your code!\n\n"
                    "❤️ Like\n"
                    "📌 Save\n"
                    "💬 Comment\n\n"
                    "Support the channel for more projects 🚀"
                )
            )
            return

        await update.message.reply_text("❌ Code not found.")
        return

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Click the GET CODE button from the channel post."
    )

# ================= ADD FILE =================

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/add project_key\n\nExample:\n/add bike_product"
        )
        return

    context.user_data["pending_key"] = context.args[0]
    await update.message.reply_text(
        f"📦 Now send the ZIP file for `{context.args[0]}`",
        parse_mode="Markdown"
    )

# ================= CAPTURE ZIP =================

async def capture_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    key = context.user_data.get("pending_key")
    if not key:
        return

    # Forward ZIP to Saved Messages
    msg = await update.message.forward(chat_id=ADMIN_ID)

    FILE_MAP[key] = msg.message_id
    context.user_data.pop("pending_key", None)

    await update.message.reply_text(
        f"✅ ZIP saved for `{key}`.\n"
        f"GET CODE button will now work.",
        parse_mode="Markdown"
    )

# ================= DELETE =================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /delete project_key")
        return

    key = context.args[0]

    if key not in FILE_MAP:
        await update.message.reply_text("❌ Key not found.")
        return

    del FILE_MAP[key]
    await update.message.reply_text(
        f"🗑️ `{key}` removed successfully.",
        parse_mode="Markdown"
    )

# ================= INIT =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(MessageHandler(filters.Document.ALL, capture_zip))

    app.run_polling()

if __name__ == "__main__":
    main()
