# Standard library
import io
import os
import unittest
import warnings
from contextlib import redirect_stderr

# Packages
import flask
import httpretty
import requests

# Local
from canonicalwebteam.search import build_search_view, NoAPIKeyError
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
        # Tests aren't where we should worry about deprication,
        # as long as everything works
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Enable HTTPretty and set up mock URLs
        httpretty.enable()
        register_uris()

        template_folder = f"{this_dir}/fixtures/templates"
        session = requests.Session()

        self.app = flask.Flask("main", template_folder=template_folder)

        # Provide fake API key
        os.environ["SEARCH_API_KEY"] = "test-api-key"

        # Default use-case
        self.app.add_url_rule(
            "/search", "search", build_search_view(session=session)
        )

        # Custom use-case
        self.app.add_url_rule(
            "/docs/search",
            "docs-search",
            build_search_view(
                session=session,
                site="maas.io/docs",
                template_path="docs/search.html",
            ),
        )

        self.client = self.app.test_client()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test_no_key(self):
        """
        Check we see the right error when there's no API key
        """

        # Delete API key
        del os.environ["SEARCH_API_KEY"]

        # Check we get 500 error without debug mode on
        output = io.StringIO()
        with redirect_stderr(output):
            error_response = self.client.get("/search?q=snap")

        self.assertIn("NoAPIKeyError", output.getvalue())
        self.assertEqual(error_response.status_code, 500)

        # Now turn debug mode on, check we get the direct error
        self.app.debug = True
        with self.assertRaises(NoAPIKeyError):
            self.app.test_client().get("/search?q=snap")

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

    def test_offset_results(self):
        """
        Check we can get offset results, starting at 20
        """

        search_response = self.client.get("/search?q=snap&start=20")

        # Check for success
        self.assertEqual(search_response.status_code, 200)
        # Check number of results
        self.assertIn(b"10 results", search_response.data)
        # Check items
        self.assertIn(
            (
                b"- https://docs.<b>snap</b>craft.io/ros-applications: "
                b"ROS applications - <b>Snap</b> documentation"
            ),
            search_response.data,
        )
        self.assertNotIn(
            b"- https://docs.<b>snap</b>craft.io/: <b>Snap</b> documentation",
            search_response.data,
        )
        # Check next page
        self.assertIn(b"Next page offset: 30", search_response.data)
        self.assertIn(b"Previous page offset: 10", search_response.data)

    def test_limited_results(self):
        """
        Check we can get a limited list of results (3)
        """

        search_response = self.client.get("/search?q=snap&start=20&num=3")

        # Check for success
        self.assertEqual(search_response.status_code, 200)
        # Check number of results
        self.assertIn(b"3 results", search_response.data)
        # Check an item
        self.assertIn(
            (
                b"- https://docs.<b>snap</b>craft.io/<b>snaps</b>hots: "
                b"Snapshots - <b>Snap</b> documentation"
            ),
            search_response.data,
        )
        self.assertNotIn(
            (
                b"- https://docs.<b>snap</b>craft.io/ros-applications: "
                b"ROS applications - <b>Snap</b> documentation"
            ),
            search_response.data,
        )
        # Check next page
        self.assertIn(b"Next page offset: 23", search_response.data)
        self.assertIn(b"Previous page offset: 17", search_response.data)

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
