# Standard library
import os

# Packages
import flask

# Local
from canonicalwebteam.search.models import get_search_results


class NoAPIKeyError(Exception):
    pass


def build_search_view(
    search_engine_id="009048213575199080868:i3zoqdwqk8o",
    template_path="search.html",
    site=None,
):
    """
    Build and return a view function that will query the
    Google Custom Search API and then render search results
    using the provided template.

    According to Google Custom API, `siteSearch` is optional.
    https://developers.google.com/custom-search/v1/using_rest#making_a_request
    Therefore, the scope of the search is determined by
    the cx (Search engine ID), this ID is public

    Usage in e.g. `app.py`:

        from canonicalwebteam.search import build_search_view

        app = Flask()
        app.add_url_rule(
            "/search",
            "search",
            build_search_view(
                search_engine_id="009048213575199080868:i3zoqdwqk8o",
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
            results = get_search_results(
                api_key=search_api_key,
                search_engine_id=search_engine_id,
                siteSearch=site_search,
                query=query,
                start=start,
                num=num,
            )

        return flask.render_template(
            template_path,
            query=query,
            start=start,
            num=num,
            results=results,
            siteSearch=site_search,
        )

    return search_view
