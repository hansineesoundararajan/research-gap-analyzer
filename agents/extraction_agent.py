import json
import logging
import re

from groq import Groq

import config


logger = logging.getLogger(__name__)


class ExtractionAgent:
    def __init__(self, client: Groq | None = None, model: str | None = None):
        self.client = client or Groq(api_key=config.settings.groq_api_key)
        self.model = model or config.settings.groq_model

    def extract_structure(self, text: str) -> dict:
        text = text[:config.settings.extraction_max_chars]

        prompt = f"""
Extract structured information from the following research paper.

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Format strictly:

{{
  "problem_statement": "",
  "methodology": "",
  "dataset": "",
  "evaluation_metrics": "",
  "key_results": "",
  "limitations": "",
  "research_gap_signals": ""
}}

Paper:
{text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Could not parse extraction JSON")
                return {"parse_error": json_str}

        return {"parse_error": content}

    def extract_from_paper(self, paper: dict) -> dict:
        authors = ", ".join(paper.get("authors", [])[:6])
        paper_text = f"""
Title: {paper.get("title", "")}
Authors: {authors}
Published: {paper.get("published", "")}
Abstract:
{paper.get("summary", "")}
"""
        structured = self.extract_structure(paper_text)
        structured["title"] = paper.get("title", "")
        structured["paper_url"] = paper.get("entry_url") or paper.get("pdf_url", "")
        return structured
