from source.data_search import *

def test_wikidata_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Wikidata')
    data = se.read_in_data()
    output = se.search_list(data, ['The Eighth Joint Conference on Lexical and Computational Semantics']) # as an example
    assert output.shape[0] > 0


def test_conferencecorpus_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Conference Corpus')
    data = se.read_in_data()
    output = se.search_list(data, ['International Conference on Construction and Real Estate Management 2017'])  # as an example
    assert output.shape[0] > 0


def test_AIDA_searchengine():
    # test if there is something wrong with the dataset or the searchengine
    pass


def test_proceedingscom_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('proceedings.com')
    data = se.read_in_data()
    output = se.search_list(data, ['COCIA'])  # as an example
    assert output.shape[0] > 0