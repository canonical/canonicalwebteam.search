def get_search_results(  # noqa: E302
    session,
    api_key,
    query,
    search_engine_id,
    start=None,
    num=None,
    siteSearch=None,
):
    """
    Query the Google Custom Search API for search results
    """

    response = session.get(
        "https://www.googleapis.com/customsearch/v1",
        params={
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "start": start,
            "num": num,
            "siteSearch": siteSearch,
        },
    )

    response.raise_for_status()

    results = response.json()

    if "items" in results:
        # Move "items" to "entries" as "items" is a method name for dicts
        results["entries"] = results.pop("items")

        # Remove newlines from the snippet
        for item in results["entries"]:
            if "htmlSnippet" in item:
                item["htmlSnippet"] = item["htmlSnippet"].replace("<br>\n", "")

    return results
