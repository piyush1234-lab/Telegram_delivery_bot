import os
import json
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
ADMIN_ID = 6803356420          # your Telegram user ID
DATA_FILE = "files.json"

# ================= LOAD STORED FILES =================

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        FILE_IDS = json.load(f)
else:
    FILE_IDS = {}

def save_files():
    with open(DATA_FILE, "w") as f:
        json.dump(FILE_IDS, f)

# ================= START (USER) =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # User came via GET CODE button
    if args and args[0] in FILE_IDS:
        await update.message.reply_document(
            document=FILE_IDS[args[0]],
            caption=(
                "🎉 Here’s your code!\n\n"
                "❤️ Like\n"
                "📌 Save\n"
                "💬 Comment\n\n"
                "Support the channel for more projects 🚀"
            )
        )
        return

    # Invalid or normal start
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Click the *GET CODE* button from the channel post "
        "to receive project files.",
        parse_mode="Markdown"
    )

# ================= ADD FILE (ADMIN ONLY) =================

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/add project_key\n\nExample:\n/add bike_product"
        )
        return

    key = context.args[0].strip()
    context.user_data["pending_key"] = key

    await update.message.reply_text(
        f"📦 Now send the ZIP file for `{key}`",
        parse_mode="Markdown"
    )

# ================= CAPTURE ZIP =================

async def capture_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    key = context.user_data.get("pending_key")
    if not key:
        return

    FILE_IDS[key] = update.message.document.file_id
    save_files()
    context.user_data.pop("pending_key", None)

    await update.message.reply_text(
        f"✅ ZIP saved for `{key}`.\n\n"
        f"You can now use this key in the posting bot.",
        parse_mode="Markdown"
    )

# ================= DELETE FILE (ADMIN ONLY) =================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/delete project_key\n\nExample:\n/delete bike_product"
        )
        return

    key = context.args[0].strip()

    if key not in FILE_IDS:
        await update.message.reply_text(
            f"❌ `{key}` not found.",
            parse_mode="Markdown"
        )
        return

    del FILE_IDS[key]
    save_files()

    await update.message.reply_text(
        f"🗑️ Deleted project `{key}` successfully.",
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
