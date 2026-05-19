import asyncio
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import RotatingFileHandler
from threading import Thread

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import config
from research_pipeline import ResearchGapPipeline


logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"Research Gap Analyzer Bot is running.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


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


def start_health_server_if_needed() -> None:
    port = os.getenv("PORT")
    if not port:
        return

    try:
        port_number = int(port)
    except ValueError:
        logger.warning("Invalid PORT value: %s", port)
        return

    server = ThreadingHTTPServer(("0.0.0.0", port_number), HealthCheckHandler)
    thread = Thread(target=server.serve_forever, daemon=True, name="health-server")
    thread.start()
    logger.info("Health server listening on port %s", port_number)


def get_webhook_settings() -> tuple[int, str, str] | None:
    external_url = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
    port = os.getenv("PORT")
    if not external_url or not port:
        return None

    try:
        port_number = int(port)
    except ValueError:
        logger.warning("Invalid PORT value: %s", port)
        return None

    url_path = os.getenv("WEBHOOK_PATH", "telegram-webhook").strip("/")
    webhook_url = f"{external_url.rstrip('/')}/{url_path}"
    return port_number, url_path, webhook_url


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
    webhook_settings = get_webhook_settings()
    if webhook_settings:
        port, url_path, webhook_url = webhook_settings
        logger.info("Running Telegram webhook on %s", webhook_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=url_path,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        start_health_server_if_needed()
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
