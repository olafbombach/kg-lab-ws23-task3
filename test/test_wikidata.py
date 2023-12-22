from source.wikidataquery import WikidataQuery

def test_wikidata_connection():
    assert (WikidataQuery.queryExample() != "")

def assess_wikidata():
    results = WikidataQuery.assess_wikidata()
    assert (int(results['number of proceedings']) >= 6782) & (int(results['number of academic conferences']) >= 8868)