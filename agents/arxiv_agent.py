import arxiv
import config

class ArxivAgent:

    def search_papers(self, query: str):
        search = arxiv.Search(
            query=query,
            max_results=config.NUM_PAPERS,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []

        for result in search.results():
            papers.append({
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary,
                "pdf_url": result.pdf_url,
                "published": result.published
            })

        return papers