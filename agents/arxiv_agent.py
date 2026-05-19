import arxiv

import config


class ArxivAgent:
    def __init__(
        self,
        num_papers: int | None = None,
        results_per_query: int | None = None,
        delay_seconds: float | None = None,
        retries: int | None = None,
    ):
        self.num_papers = num_papers or config.settings.num_papers
        self.results_per_query = results_per_query or config.settings.arxiv_results_per_query
        self.client = arxiv.Client(
            page_size=self.results_per_query,
            delay_seconds=delay_seconds or config.settings.arxiv_delay_seconds,
            num_retries=retries or config.settings.arxiv_retries,
        )

    def search_papers(self, query: str, max_results: int | None = None) -> list[dict]:
        search = arxiv.Search(
            query=query,
            max_results=max_results or self.results_per_query,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []
        for result in self.client.results(search):
            papers.append(
                {
                    "id": result.entry_id,
                    "title": result.title,
                    "authors": [a.name for a in result.authors],
                    "summary": result.summary,
                    "pdf_url": result.pdf_url,
                    "published": result.published.isoformat() if result.published else "",
                    "entry_url": result.entry_id,
                }
            )

        return papers

    def search_many(self, queries: list[str]) -> list[dict]:
        papers = []
        seen = set()

        for query in queries:
            for paper in self.search_papers(query):
                key = paper["id"] or paper["pdf_url"] or paper["title"].lower()
                if key in seen:
                    continue
                seen.add(key)
                papers.append(paper)
                if len(papers) >= self.num_papers:
                    return papers

        return papers
