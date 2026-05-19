import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import config
from research_pipeline import ResearchGapPipeline


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    level = getattr(logging, config.settings.log_level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    try:
        os.makedirs("logs", exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                "logs/bot.log",
                maxBytes=1_000_000,
                backupCount=3,
                encoding="utf-8",
            )
        )
    except OSError:
        pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=handlers,
    )


def split_message(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        while len(paragraph) > limit:
            chunks.append(paragraph[:limit])
            paragraph = paragraph[limit:]

        current = paragraph

    if current:
        chunks.append(current)

    return chunks


async def send_long_message(update: Update, text: str) -> None:
    if not update.message:
        return

    for chunk in split_message(text, config.settings.telegram_message_limit):
        await update.message.reply_text(
            chunk,
            disable_web_page_preview=True,
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(
            "Welcome to Research Gap Analyzer Bot.\n\n"
            "Send a research topic and I will retrieve arXiv papers, extract structured findings, "
            "compare them, and return research gaps with future directions."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(
            "Send a focused academic topic, for example:\n"
            "emotion-aware intelligent tutoring systems\n\n"
            "Commands:\n"
            "/start - intro\n"
            "/help - usage\n"
            "/health - bot status"
        )


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(
            f"Bot is online. Model: {config.settings.groq_model}. "
            f"Papers per report: {config.settings.num_papers}."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message or not update.message.text:
        return

    topic = update.message.text.strip()
    if len(topic) > 300:
        await update.message.reply_text("Please send a shorter, focused research topic.")
        return

    await update.message.reply_text("Searching papers and preparing the analysis. This can take a minute.")

    try:
        await update.message.chat.send_action(action=ChatAction.TYPING)
        pipeline = ResearchGapPipeline()
        analysis = await asyncio.to_thread(pipeline.analyze, topic)
        await send_long_message(update, analysis.to_text_report())
    except ValueError as exc:
        await update.message.reply_text(str(exc))
    except Exception:
        logger.exception("Analysis failed for topic: %s", topic)
        await update.message.reply_text(
            "I could not complete the analysis right now. Please try again in a few minutes "
            "or narrow the topic."
        )


def main() -> None:
    configure_logging()
    config.settings.validate_for_bot()

    app = (
        ApplicationBuilder()
        .token(config.settings.telegram_token)
        .read_timeout(90)
        .write_timeout(90)
        .connect_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Research Gap Analyzer Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
