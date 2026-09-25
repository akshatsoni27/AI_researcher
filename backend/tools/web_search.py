from ddgs import DDGS


def web_search(
    query: str,
    max_results: int = 5,
    retries: int = 2,
):
    """
    Perform a resilient web search.

    The function never crashes the research workflow because
    of a failed search. It retries with simplified queries
    and returns an empty list if all attempts fail.
    """

    queries = [
        query,
        f"{query} latest",
        query.replace("2026", "").strip(),
    ]

    # Remove duplicate queries
    unique_queries = []

    for q in queries:
        if q and q not in unique_queries:
            unique_queries.append(q)

    attempts = 0

    for search_query in unique_queries:

        if attempts >= retries + 1:
            break

        attempts += 1

        try:
            ddgs = DDGS()

            results = ddgs.text(
                search_query,
                max_results=max_results,
            )

            if not results:
                print(
                    f"\n[Web Search] No results for: "
                    f"{search_query}"
                )
                continue

            cleaned_results = []

            for result in results:

                title = result.get("title", "").strip()
                url = result.get("href", "").strip()
                snippet = result.get("body", "").strip()

                # Ignore incomplete search results
                if not title or not url:
                    continue

                cleaned_results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    }
                )

            if cleaned_results:
                return cleaned_results

        except Exception as error:

            print(
                f"\n[Web Search Warning] "
                f"Search attempt failed: {error}"
            )

    print(
        f"\n[Web Search Warning] "
        f"All search attempts failed for: {query}"
    )

    return []