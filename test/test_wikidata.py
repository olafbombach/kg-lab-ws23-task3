from source.wikidataquery import WikidataQuery


def assess_wikidata():
    results = WikidataQuery.assess_wikidata()
    assert (int(results['number of proceedings']) >= 6782) & (int(results['number of academic conferences']) >= 8868)


def creation_of_dataset():
    data = WikidataQuery.create_wikidata_dataset(overwrite_dataset=False)
    assert data.shape[0] > 8000, "The lenght does not add up"