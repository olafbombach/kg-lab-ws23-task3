from source.SearchEngine import SearchEngine
from source.Downloader import Downloader


def test_wikidata_searchengine():
    """
    First download the Wikidata dataset and then apply the SearchEngine on it.
    """
    Downloader.wikidata_downloader()

    se = SearchEngine('Wikidata')
    output = se.search_set_of_tuples({('The Eighth Joint Conference on Lexical and Computational Semantics', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0

def test_proceedingscom_searchengine():
    """
    First download the Proceedings.com dataset and then apply the SearchEngine on it.
    """
    Downloader.proceedings_downloader()

    se = SearchEngine('proceedings.com', f_search=True)
    output = se.search_set_of_tuples({('COCIA', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0