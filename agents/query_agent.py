import os
from groq import Groq
from dotenv import load_dotenv
import config

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class QueryAgent:

    def generate_queries(self, topic: str):

        prompt = f"""
Expand the following research topic into 3 optimized arXiv search queries.

Topic: {topic}

Return them strictly as a Python list.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()