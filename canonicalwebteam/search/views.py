# Standard library
import os

# Packages
import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
    request_limit="2000/day",
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

    app = flask.Flask(__name__)
    limiter = Limiter(
        get_remote_address, app=app, default_limits=[request_limit]
    )

    @limiter.limit(request_limit)
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
