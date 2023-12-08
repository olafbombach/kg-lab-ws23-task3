import json
from source.wikidataquery import WikidataQuery
from source.APICORE import APICORE



def test_COREAPIexamplequery():
    APICORE.init()
    results, elapsed = APICORE.query_api("search/data-providers", "location.countryCode:gb")
    res = json.dumps(results, indent=2)
    assert(results != "" and results != None)
