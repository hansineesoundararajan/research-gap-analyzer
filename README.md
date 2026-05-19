# Research Gap Analyzer Bot

Research Gap Analyzer Bot is a Telegram-based research assistant that turns a research topic into a structured research gap report. Send a topic, wait for the analysis, and receive a concise comparison of relevant arXiv papers with methods, datasets, limitations, research gaps, and future research directions.

It is built for students, researchers, and early-stage project builders who need a faster way to understand what has already been explored and where new work can still contribute.

## What You Can Do

- Discover relevant arXiv papers from a plain research topic
- Understand common methods, datasets, and evaluation patterns
- Identify limitations repeated across multiple papers
- Generate research gaps and future work ideas
- Receive the report directly inside Telegram
- Use it as a starting point for thesis topics, literature reviews, paper ideation, and project proposals

## How The Bot Works

1. You send a research topic in Telegram.
2. The bot creates optimized academic search queries.
3. It retrieves relevant papers from arXiv.
4. It extracts structured signals from each paper abstract.
5. It compares the papers across methodology, datasets, metrics, results, and limitations.
6. It sends back a research gap analysis report.

## Example Prompts

Send messages like these to the bot:

```text
graph neural networks for drug discovery
```

```text
emotion-aware intelligent tutoring systems
```

```text
explainable AI in healthcare diagnosis
```

```text
transformers for time series forecasting
```

For best results, use a focused academic topic instead of a very broad phrase like `AI` or `machine learning`.

## What The Report Includes

The Telegram report includes:

- Search queries used
- Papers reviewed
- Shared assumptions across papers
- Methodology patterns
- Dataset and metric patterns
- Common limitations
- Research gaps
- Future research directions
- Innovation score

## User Experience

The bot is designed to feel simple:

1. Open Telegram.
2. Send `/start`.
3. Send a research topic.
4. Wait while papers are retrieved and analyzed.
5. Read the generated research gap report.

You can also send:

```text
/health
```

to check whether the bot is online.

## Important Notes For Users

This tool is an AI research assistant, not a replacement for manual literature review. Use its output as a strong starting point, then verify papers, citations, claims, and research gaps yourself before using them in academic work.

The production Telegram flow uses paper abstracts by default instead of full PDF text. This keeps the bot faster and more reliable on free hosting.

## Tech Stack

- Python
- Telegram Bot API
- Groq API
- LLaMA 3.1 8B Instant
- arXiv API
- python-telegram-bot
- PyMuPDF for optional PDF extraction
- python-dotenv
- systemd for Oracle Cloud hosting
- Render Blueprint support

## Project Structure

```text
agents/
  arxiv_agent.py
  comparison_agent.py
  extraction_agent.py
  pdf_agent.py
  query_agent.py
config.py
main.py
research_pipeline.py
telegram_bot.py
render.yaml
requirements.txt
deploy/oracle/
```

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

## Render Free Deployment

Render is useful for a free demo deployment, but it is not true always-on hosting. Render Free Web Services spin down after inactivity. This bot runs in Telegram polling mode on Render and exposes a small health endpoint so an uptime monitor can keep the service awake.

Steps:

1. Push this repo to GitHub.
2. In Render, choose **New > Blueprint**.
3. Select this repository.
4. Render will read `render.yaml`.
5. Add the required environment variables:
   - `TELEGRAM_TOKEN`
   - `GROQ_API_KEY`
6. Deploy.

Render automatically provides `PORT`, which the bot uses for its health endpoint.

To reduce sleep-related delays, create a free uptime monitor that visits your Render service URL every 5 minutes:

```text
https://your-service-name.onrender.com/
```

Manual Render settings if not using Blueprint:

```text
Service Type: Web Service
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: python telegram_bot.py
Plan: Free
```

## Oracle Cloud Always Free Deployment

Oracle Cloud Always Free is the better option for true 24/7 hosting.

On an Ubuntu VM:

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
- `TELEGRAM_MODE`
- `WEBHOOK_URL`
- `WEBHOOK_PATH`

## Status

The bot is production-shaped for a portfolio/demo project:

- Modular agent pipeline
- Telegram interface
- arXiv retrieval
- LLM-based extraction and comparison
- Render deployment config
- Oracle `systemd` deployment config
- Environment-based secrets
- Basic logging and error handling

Future improvements could include full-PDF analysis, citation graph exploration, saved report export, a web dashboard, and stronger clustering-based similarity analysis.
