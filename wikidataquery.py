from SPARQLWrapper import SPARQLWrapper,JSON
import pandas as pan

class WikidataQuery:


  def queryWikiData(text):

    query = SPARQLWrapper("https://query.wikidata.org/sparql");

    # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
    query.setQuery(text)
    query.setReturnFormat(JSON)
    results = query.query().convert()
    return results;

  
  def queryExample():
     result = WikidataQuery.queryWikiData("""
      SELECT ?item ?itemLabel
      WHERE
      {
       ?item wdt:P31 wd:Q146 .
       SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
      }
     """)
     return result

print(WikidataQuery.queryExample())