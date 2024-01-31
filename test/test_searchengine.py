from source.data_search_opt import SearchEngine


def test_wikidata_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Wikidata')
    output = se.search_dict({'The Eighth Joint Conference on Lexical and Computational Semantics': 40})  # as an example
    assert output.shape[0] > 0


def test_conferencecorpus_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Conference Corpus')
    output = se.search_dict({'International Conference on Construction and Real Estate': 50})  # as an example
    assert output.shape[0] > 0


def test_proceedingscom_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('proceedings.com', f_search=True)
    output = se.search_dict({'COCIA': 40})  # as an example
    assert output.shape[0] > 0