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

# In-memory map (stable, no crash)
FILE_MAP = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if args and args[0] in FILE_MAP:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=FILE_MAP[args[0]],
            caption="🎉 Here’s your code!"
        )
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
    await update.message.reply_text("📦 Send the ZIP file now.")

# ================= CAPTURE ZIP =================

async def capture_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    key = context.user_data.get("pending_key")
    if not key:
        return

    FILE_MAP[key] = update.message.document.file_id
    context.user_data.pop("pending_key", None)

    await update.message.reply_text(
        f"✅ ZIP saved for `{key}`.\n"
        f"⚠️ Note: Data resets on redeploy.",
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

    if key in FILE_MAP:
        del FILE_MAP[key]
        await update.message.reply_text("🗑️ Deleted.")
    else:
        await update.message.reply_text("❌ Key not found.")

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