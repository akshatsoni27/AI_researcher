from backend.rag.vectorstore import create_vectorstore
from backend.rag.retriever import search_knowledge_base


def main():
    pdf_path = input("\nEnter PDF path:\n> ")

    print("\nIndexing PDF...")

    create_vectorstore(pdf_path)

    print("PDF indexed successfully.")

    query = input("\nAsk something about the PDF:\n> ")

    results = search_knowledge_base(query)

    print("\n" + "=" * 60)
    print("RETRIEVED EVIDENCE")
    print("=" * 60)

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")

        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")

        print("\n")
        print(result["content"][:1000])


if __name__ == "__main__":
    main()