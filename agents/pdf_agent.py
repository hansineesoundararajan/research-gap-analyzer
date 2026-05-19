import os

import fitz  # pymupdf
import requests

import config


class PDFAgent:
    def download_pdf(self, url, save_path="papers"):
        os.makedirs(save_path, exist_ok=True)

        filename = url.split("/")[-1] + ".pdf"
        filepath = os.path.join(save_path, filename)

        response = requests.get(url, timeout=config.settings.request_timeout_seconds)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath

    def extract_text(self, pdf_path):
        text = ""

        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()

        return text
