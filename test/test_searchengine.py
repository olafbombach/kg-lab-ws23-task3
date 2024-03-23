from source.SearchEngine import SearchEngine


def test_wikidata_searchengine():
    """
    Apply the SearchEngine on a random Wikidata entry.
    """
    se = SearchEngine('Wikidata')
    output = se.search_set_of_tuples({('The Eighth Joint Conference on Lexical and Computational Semantics', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0

def test_proceedingscom_searchengine():
    """
    Apply the SearchEngine on a random Proceedings.com entry.
    """
    se = SearchEngine('proceedings.com', f_search=True)
    output = se.search_set_of_tuples({('COCIA', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0