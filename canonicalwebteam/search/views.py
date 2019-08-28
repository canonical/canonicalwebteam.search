# Standard library
import os

# Packages
import flask

# Local
from canonicalwebteam.search.models import get_search_results


class NoAPIKeyError(Exception):
    pass


def build_search_view(site=None, template_path="search.html"):
    """
    Build and return a view function that will query the
    Google Custom Search API and then render search results
    using the provided template.

    Usage in e.g. `app.py`:

        from canonicalwebteam.search import build_search_view

        app = Flask()
        app.add_url_rule(
            "/search",
            "search",
            build_search_view(
                site="snapcraft.io",
                template_path="search.html"
            )
        )
    """

    def search_view():
        """
        Get search results from Google Custom Search
        """

        # The webteam's default custom search ID
        search_engine_id = "009048213575199080868:i3zoqdwqk8o"

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
