# Packages
import flask
import user_agents


def get_search_results(
    session,
    api_key,
    query,
    search_engine_id,
    site_restricted_search,
    start=None,
    num=None,
    siteSearch=None,
):
    """
    Query the Google Custom Search API for search results

    https://developers.google.com/custom-search/v1/site_restricted_api
    """

    # Block weird characters
    illegal_characters = ("【", "】")

    if any(char in query for char in illegal_characters):
        flask.abort(403, "Search query contains an illegal character")

    # Block web crawlers
    bot_prefixes = (
        "python-requests",
        "curl",
        "urlwatch",
        "GuzzleHttp",
        "Feedly",
    )
    ua_string = str(flask.request.user_agent)
    agent = user_agents.parse(ua_string)
    if agent.is_bot or ua_string.startswith(bot_prefixes):
        flask.abort(403, "Web crawlers may not perform searches")

    url_endpoint = "https://www.googleapis.com/customsearch/v1"

    if site_restricted_search:
        url_endpoint = (
            "https://www.googleapis.com/customsearch/v1/siterestrict"
        )

    response = session.get(
        url_endpoint,
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
