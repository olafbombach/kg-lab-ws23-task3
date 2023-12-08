import json
from source.wikidataquery import WikidataQuery
from source.APICORE import APICORE
from source.API import API



def test_APICORE_examplequery():
    APICORE.init()
    results, elapsed = APICORE.query_api("search/data-providers", "location.countryCode:gb")
    res = json.dumps(results, indent=2)
    assert(results != "" and results != None)


def test_API_APICORE_PAPER():
    api = API()
    assert(api.APICORE_paper("The strong Anick conjecture is true") != "")
