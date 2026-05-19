import logging
from dataclasses import dataclass

from groq import Groq

import config
from agents.arxiv_agent import ArxivAgent
from agents.comparison_agent import ComparisonAgent
from agents.extraction_agent import ExtractionAgent
from agents.query_agent import QueryAgent


logger = logging.getLogger(__name__)


@dataclass
class ResearchAnalysis:
    topic: str
    queries: list[str]
    papers: list[dict]
    structured_papers: list[dict]
    comparison_report: str

    def to_text_report(self) -> str:
        paper_lines = []
        for index, paper in enumerate(self.papers, start=1):
            authors = ", ".join(paper.get("authors", [])[:3])
            if len(paper.get("authors", [])) > 3:
                authors += ", et al."
            paper_lines.append(
                "\n".join(
                    [
                        f"{index}. {paper.get('title', 'Untitled')}",
                        f"   Authors: {authors or 'Not listed'}",
                        f"   Published: {paper.get('published', 'Not listed')}",
                        f"   Link: {paper.get('entry_url') or paper.get('pdf_url', '')}",
                    ]
                )
            )

        queries = "\n".join(f"- {query}" for query in self.queries)
        papers = "\n\n".join(paper_lines)

        return f"""Research Gap Analysis Report

Topic:
{self.topic}

Search Queries Used:
{queries}

Papers Reviewed:
{papers}

Cross-Paper Analysis:
{self.comparison_report}
"""


class ResearchGapPipeline:
    def __init__(self, settings: config.Settings | None = None):
        self.settings = settings or config.settings
        self.settings.validate_for_bot()

        client = Groq(api_key=self.settings.groq_api_key)
        self.query_agent = QueryAgent(client=client, model=self.settings.groq_model)
        self.arxiv_agent = ArxivAgent(
            num_papers=self.settings.num_papers,
            results_per_query=self.settings.arxiv_results_per_query,
            delay_seconds=self.settings.arxiv_delay_seconds,
            retries=self.settings.arxiv_retries,
        )
        self.extraction_agent = ExtractionAgent(client=client, model=self.settings.groq_model)
        self.comparison_agent = ComparisonAgent(client=client, model=self.settings.groq_model)

    def analyze(self, topic: str) -> ResearchAnalysis:
        topic = " ".join(topic.strip().split())
        if len(topic) < 3:
            raise ValueError("Please send a more specific research topic.")

        logger.info("Generating search queries for topic: %s", topic)
        queries = self.query_agent.generate_queries(topic)

        logger.info("Searching arXiv with %s queries", len(queries))
        papers = self.arxiv_agent.search_many(queries)
        if not papers:
            raise RuntimeError("No relevant arXiv papers were found for this topic.")

        logger.info("Extracting structured data from %s papers", len(papers))
        structured_papers = [
            self.extraction_agent.extract_from_paper(paper)
            for paper in papers
        ]

        logger.info("Running cross-paper comparison")
        comparison_report = self.comparison_agent.compare_papers(structured_papers)

        return ResearchAnalysis(
            topic=topic,
            queries=queries,
            papers=papers,
            structured_papers=structured_papers,
            comparison_report=comparison_report,
        )
