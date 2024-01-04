from source.data_search import *

def test_wikidata_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Wikidata')
    output = se.search_list(['The Eighth Joint Conference on Lexical and Computational Semantics']) # as an example
    assert output.shape[0] > 0


def test_conferencecorpus_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('Conference Corpus')
    output = se.search_list(['International Conference on Construction and Real Estate Management 2017'])  # as an example
    assert output.shape[0] > 0


def test_AIDA_searchengine():
    # test if there is something wrong with the dataset or the searchengine
    pass


def test_proceedingscom_searchengine():
    # test if there is something wrong with the dataset or the searchengine

    se = SearchEngine('proceedings.com')
    output = se.search_list(['COCIA'])  # as an example
    assert output.shape[0] > 0