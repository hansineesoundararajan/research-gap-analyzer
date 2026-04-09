import os
import requests
import fitz  # pymupdf


class PDFAgent:

    def download_pdf(self, url, save_path="papers"):
        os.makedirs(save_path, exist_ok=True)

        filename = url.split("/")[-1] + ".pdf"
        filepath = os.path.join(save_path, filename)

        response = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text()

        return text