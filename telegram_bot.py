import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to Research Gap Analyzer Bot!\n\n"
        "Send me a research topic and I will analyze research gaps."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text

    await update.message.reply_text("🔍 Fetching research papers...")

    # 1️⃣ Fetch arXiv papers
    arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results=3"
    response = requests.get(arxiv_url)

    # Simple fallback summary (no XML parsing for now)
    papers_text = response.text[:3000]

    await update.message.reply_text("🧠 Running strategic analysis...")

    # 2️⃣ Call Groq
    groq_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "user",
                    "content": f"""
You are a research strategist.

Analyze research gaps for the topic:
{topic}

Based on:
{papers_text}

Provide:
1. Core themes
2. Blind spots
3. Research gaps
4. 2 novel research directions
5. Innovation score (0-1)
"""
                }
            ],
            "temperature": 0,
        },
    )

    analysis = groq_response.json()["choices"][0]["message"]["content"]

    await update.message.reply_text(analysis[:4000])  # Telegram limit


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()