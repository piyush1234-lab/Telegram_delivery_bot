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

# In-memory storage: project_key -> file_id
FILE_MAP = {}

# ================= START / DELIVERY =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Public delivery flow
    if args and args[0] in FILE_MAP:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=FILE_MAP[args[0]],
            caption="🎉 Here’s your file!"
        )
        return

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Please click the GET CODE button from the channel post."
    )

# ================= ADD =================

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/add project_key\n\nExample:\n/add bike_project"
        )
        return

    key = context.args[0]

    if key in FILE_MAP:
        await update.message.reply_text(
            "❌ This key already exists.\n"
            "Use /edit to replace the file."
        )
        return

    context.user_data["pending_add"] = key
    await update.message.reply_text("📦 Send the document file now.")

# ================= EDIT =================

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/edit project_key"
        )
        return

    key = context.args[0]

    if key not in FILE_MAP:
        await update.message.reply_text(
            "❌ This key does not exist.\n"
            "Use /add to create it first."
        )
        return

    context.user_data["pending_edit"] = key
    await update.message.reply_text(
        "✏️ Send the new document to replace the existing file."
    )

# ================= CAPTURE DOCUMENT =================

async def capture_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    doc = update.message.document
    if not doc:
        return

    # ADD flow
    if "pending_add" in context.user_data:
        key = context.user_data.pop("pending_add")
        FILE_MAP[key] = doc.file_id

        await update.message.reply_text(
            f"✅ File added for `{key}`.\n"
            f"⚠️ Data resets on bot restart.",
            parse_mode="Markdown"
        )
        return

    # EDIT flow
    if "pending_edit" in context.user_data:
        key = context.user_data.pop("pending_edit")
        FILE_MAP[key] = doc.file_id

        await update.message.reply_text(
            f"🔁 File replaced for `{key}`.\n"
            f"⚠️ Data resets on bot restart.",
            parse_mode="Markdown"
        )
        return

# ================= DELETE =================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/delete project_key"
        )
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
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(MessageHandler(filters.Document.ALL, capture_document))

    app.run_polling()

if __name__ == "__main__":
    main()