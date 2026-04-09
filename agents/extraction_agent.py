import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ExtractionAgent:

    def extract_structure(self, text):

        # Limit text to avoid token overflow
        text = text[:12000]

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
  "limitations": ""
}}

Paper:
{text}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # 🔎 Extract JSON safely using bracket detection
        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except:
                return {"parse_error": json_str}

        return {"parse_error": content}