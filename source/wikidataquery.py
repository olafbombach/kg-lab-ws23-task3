from SPARQLWrapper import SPARQLWrapper,JSON
import pandas as pan
import json

class WikidataQuery:

  def queryWikiData(text):

    query = SPARQLWrapper("https://query.wikidata.org/sparql");

    # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
    query.setQuery(text)
    query.setReturnFormat(JSON)
    results = query.query().convert()
    return results

  
  def queryExample():
      text = '''
            SELECT ?item ?itemLabel
            WHERE {?item wdt:P31 wd:Q146.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
            }'''
      result = WikidataQuery.queryWikiData(text)
      return result

  def how_many_proceedings():
      # How many entries exist in Wikidata that have the property: instance of 'proceedings' (Q1143604)
      text = '''
            SELECT (COUNT (?proceeding) AS ?count)
            WHERE {?proceeding wdt:P31 wd:Q1143604.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }'''
      output = WikidataQuery.queryWikiData(text)
      result = output['results']['bindings'][0]['count']['value']
      return result

  def how_many_academic_conferences():
      # How many entries exist in Wikidata that have the property: instance of 'academic conference' (Q2020153)
      text = '''
            SELECT (COUNT (?conferences) AS ?count)
            WHERE {?conferences wdt:P31 wd:Q2020153.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }'''
      output = WikidataQuery.queryWikiData(text)
      result = output['results']['bindings'][0]['count']['value']
      return result

  def assess_wikidata():
      pro = WikidataQuery.how_many_proceedings()
      ac = WikidataQuery.how_many_academic_conferences()

      assess_dict = {'number of proceedings': pro, 'number of academic conferences': ac}
      assess_json = json.dumps(assess_dict, indent=2)
      with open('..\\results\\wikidata_assessment.json', 'w') as outfile:
          outfile.write(assess_json)

      return assess_json

print(WikidataQuery.assess_wikidata())