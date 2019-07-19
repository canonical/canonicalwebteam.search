# Standard library
import os
import unittest
import warnings

# Packages
import flask
import httpretty

# Local
from canonicalwebteam.search import build_search_view
from tests.fixtures.search_mock import register_uris


this_dir = os.path.dirname(os.path.realpath(__file__))


class TestApp(unittest.TestCase):
    def setUp(self):
        """
        Set up Flask app with build_search_view extension for testing
        And set up mocking for googleapis.com
        """

        # Suppress annoying warnings from HTTPretty
        # See: https://github.com/gabrielfalcao/HTTPretty/issues/368
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed.*"
        )

        # Enable HTTPretty and set up mock URLs
        httpretty.enable()
        register_uris()

        template_folder = f"{this_dir}/fixtures/templates"

        app = flask.Flask("main", template_folder=template_folder)

        # Provide fake API key
        os.environ["SEARCH_API_KEY"] = "test-api-key"

        # Default use-case
        app.add_url_rule("/search", "search", build_search_view())

        # Custom use-case
        app.add_url_rule(
            "/docs/search",
            "docs-search",
            build_search_view(
                site="maas.io/docs", template_path="docs/search.html"
            ),
        )

        self.client = app.test_client()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test_no_search(self):
        """
        Check the search page displays when no query is provided
        """

        search_response = self.client.get("/search")
        docs_response = self.client.get("/docs/search")

        # Check for success
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(docs_response.status_code, 200)

        # Check content
        self.assertIn(b"No results", search_response.data)
        self.assertIn(b"No docs results", docs_response.data)

    def test_first_page_of_results(self):
        """
        Check that the first page works as expected
        """

        search_response = self.client.get("/search?q=snap")

        # Check for success
        self.assertEqual(search_response.status_code, 200)
        # Check number of results
        self.assertIn(b"10 results", search_response.data)
        # Check an item
        self.assertIn(
            b"- https://docs.<b>snap</b>craft.io/: <b>Snap</b> documentation",
            search_response.data,
        )
        # Check next page
        self.assertIn(b"Next page offset: 11", search_response.data)
        self.assertNotIn(b"Previous", search_response.data)

    def test_first_page_of_docs_results(self):
        """
        Check that the first page of docs results has docs search content
        """
        docs_response = self.client.get("/docs/search?q=snap")
        # Check for success
        self.assertEqual(docs_response.status_code, 200)
        # check the number of results
        self.assertIn(b"10 docs results", docs_response.data)
        # Check an item
        self.assertIn(
            (
                b"- https://maas.io/docs/2.3/en/nodes-add: "
                b"Add Nodes | MAAS documentation"
            ),
            docs_response.data,
        )
        self.assertNotIn(
            b"- https://docs.snapcraft.io/: <b>Snap</b> documentation",
            docs_response.data,
        )
        # Check next page
        self.assertIn(b"Next docs page offset: 11", docs_response.data)
        self.assertNotIn(b"Previous", docs_response.data)
