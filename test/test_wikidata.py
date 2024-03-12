from source.UpdateSources import WikidataQuery


def test_wikidata_connection():
    """
    Tests if there is a connection to Wikidata and if SparQL works properly.
    """
    results = WikidataQuery.queryExample()
    assert type(results) is not None

def test_wikidata_assessment():
    """
    Assesses some parameters for Wikidata.
    """
    dict_result = WikidataQuery.assess_wikidata(write_to_json=False)
    assert int(dict_result['number of proceedings']) > 5000
    assert int(dict_result['number of academic conferences']) > 5000
