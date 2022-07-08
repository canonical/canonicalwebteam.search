# Standard library
import os

# Packages
import flask
import user_agents
from pydnsbl import DNSBLIpChecker

# Local
from canonicalwebteam.search.models import get_search_results


class NoAPIKeyError(Exception):
    pass


def build_search_view(
    session,
    site=None,
    template_path="search.html",
    search_engine_id="009048213575199080868:i3zoqdwqk8o",
    site_restricted_search=False,
):
    """
    Build and return a view function that will query the
    Google Custom Search API and then render search results
    using the provided template.

    Usage in e.g. `app.py`:

        from canonicalwebteam.search import build_search_view

        app = Flask()
        session = talisker.requests.get_session()
        app.add_url_rule(
            "/search",
            "search",
            build_search_view(
                session=session,
                site="snapcraft.io",
                template_path="search.html"
            )
        )
    """

    def search_view():
        """
        Get search results from Google Custom Search
        """

        # API key should always be provided as an environment variable
        search_api_key = os.getenv("SEARCH_API_KEY")

        if not search_api_key:
            raise NoAPIKeyError("Unable to search: No API key provided")

        params = flask.request.args
        query = params.get("q")
        start = params.get("start")
        num = params.get("num")
        site_search = site or params.get("siteSearch") or params.get("domain")
        results = None

        if query:
            # Block weird characters
            illegal_characters = ("【", "】")

            if any(char in query for char in illegal_characters):
                flask.abort(403, "Search query contains an illegal character")

            # Block spammers from blacklists
            if ".com" in query:
                ipcheck = DNSBLIpChecker().check(flask.request.remote_addr)
                if ipcheck.blacklisted:
                    blacklists = ", ".join(ipcheck.detected_by.keys())
                    flask.abort(
                        403, f"IP address detected in blacklists: {blacklists}"
                    )

            # Block if a search bot
            agent = user_agents.parse(str(flask.request.user_agent))
            if agent.is_bot:
                flask.abort(
                    403, "Search engine crawlers can't perform searches"
                )

            results = get_search_results(
                session=session,
                api_key=search_api_key,
                search_engine_id=search_engine_id,
                siteSearch=site_search,
                site_restricted_search=site_restricted_search,
                query=query,
                start=start,
                num=num,
            )

            return (
                flask.render_template(
                    template_path,
                    query=query,
                    start=start,
                    num=num,
                    results=results,
                    siteSearch=site_search,
                ),
                {"X-Robots-Tag": "noindex"},
            )

        else:
            return flask.render_template(
                template_path,
                query=query,
                start=start,
                num=num,
                results=results,
                siteSearch=site_search,
            )

    return search_view
