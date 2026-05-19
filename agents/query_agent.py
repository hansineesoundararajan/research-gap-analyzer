import ast
import json
import logging
import re

from groq import Groq

import config


logger = logging.getLogger(__name__)


class QueryAgent:
    def __init__(self, client: Groq | None = None, model: str | None = None):
        self.client = client or Groq(api_key=config.settings.groq_api_key)
        self.model = model or config.settings.groq_model

    def generate_queries(self, topic: str) -> list[str]:
        topic = topic.strip()
        if not topic:
            return []

        prompt = f"""
Expand the following research topic into 3 optimized arXiv search queries.

Topic: {topic}

Return ONLY a JSON array of strings.
Do not add markdown or explanation.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        queries = self._parse_queries(content)

        candidates = [topic, *queries]
        deduped = []
        seen = set()
        for query in candidates:
            clean = " ".join(query.split())
            key = clean.lower()
            if clean and key not in seen:
                seen.add(key)
                deduped.append(clean)

        return deduped[:4]

    @staticmethod
    def _parse_queries(content: str) -> list[str]:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            try:
                parsed = ast.literal_eval(match.group(0))
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if str(item).strip()]
            except (SyntaxError, ValueError):
                logger.warning("Could not parse query list from LLM output")

        return []
