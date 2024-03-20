from source.SearchEngine import SearchEngine


def test_wikidata_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Wikidata')
    output = se.search_set_of_tuples({('The Eighth Joint Conference on Lexical and Computational Semantics', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0

def test_proceedingscom_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('proceedings.com', f_search=True)
    output = se.search_set_of_tuples({('COCIA', 'title', 1.0)})  # as an example
    assert output.shape[0] > 0