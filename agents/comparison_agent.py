import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ComparisonAgent:

    def compare_papers(self, structured_papers):

        prompt = f"""
You are an advanced research strategist and innovation analyst.

Below are structured summaries of multiple research papers.

Your task is NOT to summarize them individually.

Instead, perform deep cross-paper synthesis:

1. Identify shared research assumptions across papers.
2. Identify overlapping methodological strategies.
3. Detect conceptual blind spots common to all papers.
4. Identify dimensions of knowledge gap detection NOT collectively addressed.
5. Synthesize 3 novel research opportunities that extend beyond current approaches.
6. Provide a Field Innovation Score (0–1):
   - 0 → Highly saturated field
   - 1 → Large unexplored research potential

Be analytical and synthesis-focused.
Avoid repeating paper summaries.
Focus on higher-level reasoning and systemic gaps.

Return output in clearly separated structured sections with headings.

Papers:
{json.dumps(structured_papers, indent=2)}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()