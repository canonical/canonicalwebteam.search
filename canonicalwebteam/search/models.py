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
        "python",  # python-requests/, python-urllib3/, Python/ etc.
        "Go-http-client",
        "kube-probe",
        "Prometheus",
        "curl",
        "urlwatch",
        "GuzzleHttp",
        "Feedly",
        "github-camo",
        "Site24x7",
        "check_http",
        "Tiny Tiny RSS",
        "RSS Discovery Engine",
        "NetNewsWire",
        "ALittle Client",
    )
    bot_contains = ("HeadlessChrome/", "Assetnote/")
    agent = user_agents.parse(str(flask.request.user_agent))
    if (
        agent.is_bot
        or agent.ua_string.startswith(bot_prefixes)
        or any(substr in agent.ua_string for substr in bot_contains)
    ):
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
