import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, CHANNEL_LINK, DEVELOPER_NAME, DEVELOPER_CHAT_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

NAME, PROJECT, WHATSAPP, EMAIL, CONFIRM = range(5)

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Start Karo", callback_data="start_intake")],
        [InlineKeyboardButton("Mere Projects Dekho", url=CHANNEL_LINK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome = (
        f"Hey {user.first_name}! 👋\n\n"
        f"Main **{DEVELOPER_NAME}** ka Client Bot hoon.\n\n"
        f"Mujhe apni project details do, main sab manage kar lunga.\n"
        f"Neeche button dabao ya `/project` likho."
    )

    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")
    return ConversationHandler.END


async def start_intake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Alright! Chalo shuru karte hain. 🚀\n\n"
        "**Step 1/4:** Apna **naam** batao.",
        parse_mode="Markdown",
    )
    return NAME


async def project_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Alright! Chalo shuru karte hain. 🚀\n\n"
        "**Step 1/4:** Apna **naam** batao.",
        parse_mode="Markdown",
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[update.effective_user.id] = {"name": update.message.text}
    await update.message.reply_text(
        f"Hi {update.message.text}! 👋\n\n"
        "**Step 2/4:** Kya **banwana chahte ho**? Detail me batao.",
        parse_mode="Markdown",
    )
    return PROJECT


async def get_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[update.effective_user.id]["project"] = update.message.text
    await update.message.reply_text(
        "**Step 3/4:** Apna **WhatsApp number** do (+91 format me).",
        parse_mode="Markdown",
    )
    return WHATSAPP


async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[update.effective_user.id]["whatsapp"] = update.message.text
    await update.message.reply_text(
        "**Step 4/4:** Apna **email address** do.",
        parse_mode="Markdown",
    )
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]["email"] = update.message.text

    data = user_data[user_id]

    summary = (
        "📋 **Tumhara Summary:**\n\n"
        f"👤 **Naam:** {data['name']}\n"
        f"💻 **Project:** {data['project']}\n"
        f"📱 **WhatsApp:** {data['whatsapp']}\n"
        f"📧 **Email:** {data['email']}\n\n"
        "Ye details sahi hain?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Haan, Bhejo", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Nahi, Cancel", callback_data="confirm_no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = user_data.get(user_id)

    if query.data == "confirm_yes" and data:
        # Channel ko message bhejo
        channel_msg = (
            "🆕 **NEW CLIENT REQUEST**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Naam:** {data['name']}\n"
            f"📱 **WhatsApp:** {data['whatsapp']}\n"
            f"📧 **Email:** {data['email']}\n\n"
            f"💻 **Project Details:**\n{data['project']}\n\n"
            f"🔗 **Client TG:** [{query.from_user.first_name}](tg://user?id={user_id})\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )

        try:
            await context.bot.send_message(
                chat_id=DEVELOPER_CHAT_ID,
                text=channel_msg,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Developer ko bhejne me error: {e}")

        # Client ko channel link do
        keyboard = [
            [InlineKeyboardButton("Join My Channel", url=CHANNEL_LINK)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Sab kuch sahi hai! ✅\n\n"
            "Details bhej diye hain. Jaldi se contact karunga.\n\n"
            "Tab tak mere channel ko join karo - wahan mere "
            "sabhi projects milenge!",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

        logger.info(f"Naya client: {data['name']} | {data['whatsapp']} | {data['email']}")
        del user_data[user_id]

    elif query.data == "confirm_no":
        if user_id in user_data:
            del user_data[user_id]
        await query.edit_message_text(
            "Cancel kar diya. 🔙\n"
            "Dobur se shuru karne ke liye `/project` likho."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id in user_data:
        del user_data[user_id]
    await update.message.reply_text("Cancel kar diya. Dobur se shuru karne ke liye `/start` likho.")
    return ConversationHandler.END


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: `{chat_id}`", parse_mode="Markdown")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("project", project_command),
            CallbackQueryHandler(start_intake, pattern="^start_intake$"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_whatsapp)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            CONFIRM: [CallbackQueryHandler(confirm, pattern="^(confirm_yes|confirm_no)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(conv_handler)

    print("Bot chal raha hai... 🚀")
    print("Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
