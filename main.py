from research_pipeline import ResearchGapPipeline


def main():
    print("=== AURA-Research: Autonomous Paper Agent ===")

    topic = input("Enter research topic: ")
    report = ResearchGapPipeline().analyze(topic)
    print(report.to_text_report())


if __name__ == "__main__":
    main()
