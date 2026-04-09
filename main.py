from agents.query_agent import QueryAgent
from agents.arxiv_agent import ArxivAgent
from agents.pdf_agent import PDFAgent
from agents.extraction_agent import ExtractionAgent
from agents.comparison_agent import ComparisonAgent


def main():
    print("=== AURA-Research: Autonomous Paper Agent ===")

    topic = input("Enter research topic: ")

    # 1️⃣ Generate search queries
    query_agent = QueryAgent()
    queries = query_agent.generate_queries(topic)

    print("\nGenerated Queries:")
    print(queries)

    # 2️⃣ Fetch papers from arXiv
    arxiv_agent = ArxivAgent()
    papers = arxiv_agent.search_papers(topic)

    print("\nFetching Papers...")

    for i, paper in enumerate(papers):
        print(f"\nPaper {i+1}")
        print("Title:", paper["title"])
        print("Authors:", paper["authors"])
        print("Published:", paper["published"])
        print("PDF:", paper["pdf_url"])

    # 3️⃣ Initialize agents
    pdf_agent = PDFAgent()
    extraction_agent = ExtractionAgent()

    all_structured_data = []

    # 4️⃣ Download, extract, and structure papers
    for paper in papers:
        print(f"\nDownloading: {paper['title']}")

        pdf_path = pdf_agent.download_pdf(paper["pdf_url"])
        text = pdf_agent.extract_text(pdf_path)

        print("Extracted text length:", len(text))

        structured_data = extraction_agent.extract_structure(text)

        print("\nStructured Extraction:")
        print(structured_data)

        all_structured_data.append(structured_data)

    # 5️⃣ Cross-paper comparison
    print("\n=== Cross-Paper Comparative Analysis ===")

    comparison_agent = ComparisonAgent()
    comparison_report = comparison_agent.compare_papers(all_structured_data)

    print(comparison_report)


if __name__ == "__main__":
    main()