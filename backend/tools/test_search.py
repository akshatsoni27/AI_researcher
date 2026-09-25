from backend.tools.web_search import web_search


def main():
    query = input("\nSearch the web:\n> ")

    results = web_search(query)

    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)

    for index, result in enumerate(results, start=1):
        print(f"\n{index}. {result['title']}")
        print(f"URL: {result['url']}")
        print(f"{result['snippet']}")


if __name__ == "__main__":
    main()