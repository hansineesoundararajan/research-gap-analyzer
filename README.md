# Research Gap Analyzer Bot

An autonomous Telegram bot that takes a research topic, retrieves relevant arXiv papers, extracts structured academic signals with Groq/LLaMA, compares papers, and returns research gaps plus future research directions.

## What It Does

- Generates optimized academic search queries
- Retrieves relevant papers from arXiv
- Extracts methodology, datasets, metrics, results, limitations, and gap signals
- Performs cross-paper comparative analysis
- Sends a structured research gap report through Telegram
- Runs as a long-lived service on an Oracle Cloud Always Free VM

## Tech Stack

- Python
- Telegram Bot API
- Groq API
- LLaMA 3.1 8B Instant
- arXiv API
- python-telegram-bot
- PyMuPDF for optional PDF extraction
- python-dotenv
- systemd for 24/7 Oracle Cloud hosting

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
```

Run the Telegram bot:

```bash
python telegram_bot.py
```

Run the terminal version:

```bash
python main.py
```

## Oracle Cloud Always Free Deployment

Recommended deployment target: an Ubuntu VM on Oracle Cloud Always Free.

On the VM:

```bash
sudo apt-get update
sudo apt-get install -y git
git clone YOUR_REPO_URL research-gap-analyzer
cd research-gap-analyzer
bash deploy/oracle/setup_oracle_ubuntu.sh
nano .env
sudo systemctl start research-gap-bot.service
sudo systemctl status research-gap-bot.service
```

Useful service commands:

```bash
sudo systemctl restart research-gap-bot.service
sudo journalctl -u research-gap-bot.service -f
```

## Environment Variables

Required:

- `TELEGRAM_TOKEN`
- `GROQ_API_KEY`

Optional:

- `GROQ_MODEL`
- `NUM_PAPERS`
- `ARXIV_RESULTS_PER_QUERY`
- `ARXIV_DELAY_SECONDS`
- `ARXIV_RETRIES`
- `EXTRACTION_MAX_CHARS`
- `TELEGRAM_MESSAGE_LIMIT`
- `REQUEST_TIMEOUT_SECONDS`
- `LOG_LEVEL`

## Notes

The production Telegram flow uses abstracts by default instead of downloading full PDFs. This keeps responses fast and reliable on a small free VM. PDF extraction remains available through `PDFAgent` for future expansion.
