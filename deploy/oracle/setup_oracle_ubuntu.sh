#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
SERVICE_USER="${SERVICE_USER:-ubuntu}"
SERVICE_NAME="research-gap-bot.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

if [[ ! -f "${PROJECT_DIR}/requirements.txt" ]]; then
  echo "Run this script from the project root, or set PROJECT_DIR=/path/to/project."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git

python3 -m venv "${PROJECT_DIR}/.venv"
"${PROJECT_DIR}/.venv/bin/python" -m pip install --upgrade pip
"${PROJECT_DIR}/.venv/bin/python" -m pip install -r "${PROJECT_DIR}/requirements.txt"

if [[ ! -f "${PROJECT_DIR}/.env" ]]; then
  cp "${PROJECT_DIR}/.env.example" "${PROJECT_DIR}/.env"
  echo "Created .env. Edit it with TELEGRAM_TOKEN and GROQ_API_KEY before starting the service."
fi

sudo sed \
  -e "s|User=ubuntu|User=${SERVICE_USER}|g" \
  -e "s|/opt/research-gap-analyzer|${PROJECT_DIR}|g" \
  "${PROJECT_DIR}/deploy/oracle/research-gap-bot.service" | sudo tee "${SERVICE_FILE}" >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"

echo "Setup complete."
echo "Edit ${PROJECT_DIR}/.env, then run:"
echo "  sudo systemctl start ${SERVICE_NAME}"
echo "  sudo systemctl status ${SERVICE_NAME}"
