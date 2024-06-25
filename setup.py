#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.search",
    version="1.3.1",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    url="https://github.com/canonical/canonicalwebteam.search",
    description=(
        "Flask extension to provide a search view for querying the webteam's "
        "Google Custom Search account"
    ),
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["canonicalwebteam.flask-base>=1.1.0", "user-agents>=2.0.0", "Flask-Limiter>=2.9.0"],
    tests_require=["httpretty"],
)
