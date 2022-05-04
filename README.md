# canonicalwebteam.search

[![circleci build status](https://circleci.com/gh/canonical-web-and-design/canonicalwebteam.search.svg?style=shield)](https://circleci.com/gh/canonical-web-and-design/canonicalwebteam.search)
[![Code coverage](https://codecov.io/gh/canonical-web-and-design/canonicalwebteam.search/branch/main/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/canonicalwebteam.search)
[![PyPI version](https://badge.fury.io/py/canonicalwebteam.search.svg)](https://pypi.org/project/canonicalwebteam.search/)

Flask extension to provide a search view for querying the webteam's Google Custom Search account.

## Installation

`pip3 install canonicalwebteam.search`

Or add `canonicalwebteam.search` to your `requirements.txt`.

## Usage

### Application code

You can add the extension on your project's application as follows:

``` python3
import talisker.requests
from flask import Flask
from canonicalwebteam.search import build_search_view

app = Flask("myapp")
session = talisker.requests.get_session()  # You must provide a requests session

app.add_url_rule("/search", "search", build_search_view(session))

# Or, a bit more complex example

app.add_url_rule(
    "/docs/search",
    "docs-search",
    build_search_view(
        session=session,
        site="maas.io/docs",
        template_path="docs/search.html"
        search_engine_id="xxxxxxxxxx" # Optional argument, required by some of our sites
    )
)
```

[![Publish](https://github.com/canonical-web-and-design/canonicalwebteam.search/actions/workflows/publish.yaml/badge.svg?branch=main)](https://github.com/canonical-web-and-design/canonicalwebteam.search/actions/workflows/publish.yaml)

### The template

You need to create an HTML template at the specificed `template_path`. By default this will be `search.html` inside your templates folder. This template will be passed the following data:

- `{{ query }}` - the contents of the `q=` search query parameter
- `{{ start }}` - the contents of the `start=` query parameter - the offset at which to start returning results (used for pagination - default 0)
- `{{ num }}` - the contents of the `num=` query parameter - the number of search results to return  (default 10)
- `{{ results }}` - the results returned from the Google Custom Search query. The actual search results are in `{{ results.entries }}`.

### The API key

You then need to provide the API key for the Google Custom Search API  as an environment variable called `SEARCH_API_KEY` when the server starts - e.g.:

```
SEARCH_API_KEY=xxxxx FLASK_APP=app.py flask run
```

Once this is done, you should be able to visit `/search?q={some_query}` in your site and see search results built with your `search.html` template.

For some sites, you will need to pass a specific search engine ID (cx) to the `build_search_view` which you will find in the [Custom Search Engine page](https://cse.google.co.uk/cse/all).

## New sites

If you created a new site and the API is not returning any results, you may need to add it to the Google Custom Search Engine [list of sites](https://cse.google.com/cse/all). If you don't see any sites in this page, ask the Webteam.
