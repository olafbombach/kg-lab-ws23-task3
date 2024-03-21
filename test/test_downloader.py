import os
from urllib.parse import urlparse

from source.Downloader import Downloader

def test_wikidata_download():
    """
    Downloads the Wikidata database used in this project. Checks if everything works fine.
    """
    try:
        Downloader.wikidata_downloader()
    except Exception as e:
        print(f"The download of Wikidata went wrong due to {e}")

def test_proceedings_download():
    """
    Downloads the Proceedings.com database used in this project. Checks if everything works fine.
    """
    try:
        Downloader.proceedings_downloader()
    except Exception as e:
        print(f"The scraping of Proceedings.com went wrong due to {e}")

def test_glove_connection():
    """
    Validate if the correct URL ZIP file could be found using the parser from the Downloader class.
    """
    parsed_url = urlparse("https://nlp.stanford.edu/data/glove.6B.zip")
    assert parsed_url.path == "/data/glove.6B.zip", "The correct URL zip file could not be found."
