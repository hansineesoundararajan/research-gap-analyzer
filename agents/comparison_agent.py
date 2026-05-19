import json

from groq import Groq

import config


class ComparisonAgent:
    def __init__(self, client: Groq | None = None, model: str | None = None):
        self.client = client or Groq(api_key=config.settings.groq_api_key)
        self.model = model or config.settings.groq_model

    def compare_papers(self, structured_papers: list[dict]) -> str:
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
6. Provide a Field Innovation Score (0-1):
   - 0 = Highly saturated field
   - 1 = Large unexplored research potential

Be analytical and synthesis-focused.
Avoid repeating paper summaries.
Focus on higher-level reasoning and systemic gaps.

Return output in clearly separated structured sections with headings:
- Shared Assumptions
- Methodology Patterns
- Dataset and Metric Patterns
- Common Limitations
- Research Gaps
- Future Research Directions
- Innovation Score

Papers:
{json.dumps(structured_papers, indent=2)}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        return response.choices[0].message.content.strip()
