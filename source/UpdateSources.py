from SPARQLWrapper import SPARQLWrapper, JSON
from source.HelperFunctions import find_root_directory
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

class WikidataQuery(object):
    """
        An operator that enables to query from wikidata.
        It comes with some additional methods that can display the current status of wikidata conference entries.
        It further creates the dataset used for the data synchronization.
    """

    # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
    query = SPARQLWrapper("https://query.wikidata.org/sparql")
    root_dir = find_root_directory()
    path_to_results = root_dir / "results"
    path_to_datasets = root_dir / "datasets" / "wikidata"

    @staticmethod
    def queryWikiData(input_text: str):
        """
        The method to query using SPARQLWrapper.
        """
        WikidataQuery.query.setQuery(input_text)
        WikidataQuery.query.setReturnFormat(JSON)
        results = WikidataQuery.query.query().convert()
        return results

    @staticmethod
    def queryExample():
        """
        Example query searching for entries in Wikidata that are house cats (property).
        """
        text = '''
                SELECT ?item ?itemLabel
                WHERE {?item wdt:P31 wd:Q146.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
                }'''
        result = WikidataQuery.queryWikiData(text)
        return result

    @staticmethod
    def assess_wikidata(write_to_json: bool) -> dict:
        """
            This method calls all Wikidata assessment methods and writes a json-file to results.
        """
        pro = WikidataQuery._how_many_proceedings()
        ac = WikidataQuery._how_many_academic_conferences()

        assess_dict = {'number of proceedings': pro, 
                       'number of academic conferences': ac}
        assess_json = json.dumps(assess_dict, indent=2)

        if write_to_json:
            WikidataQuery._write_json_to_results(assess_json, 'wikidata_assessment')
        else:
            pass

        return assess_dict

    @staticmethod
    def create_wikidata_dataset(overwrite_dataset: bool = False) -> pd.DataFrame:
        """
            This method (query) gets all conferences and their information as a pandas DataFrame.
            It further directly overwrites the dataset-file for wikidata.
        """
        text = '''
                SELECT ?conferencesLabel ?title ?countryLabel ?locationLabel ?main_subjectLabel ?start_time ?end_time ?seriesLabel 
                ?short_name ?beginnings ?WikiCFP_identifier ?DBLP_identifier
                
                WHERE {?conferences wdt:P31 wd:Q2020153.                
                OPTIONAL { ?conferences wdt:P1476 ?title. }
                OPTIONAL { ?conferences wdt:P17 ?country. }
                OPTIONAL { ?conferences wdt:P276 ?location. }
                OPTIONAL { ?conferences wdt:P921 ?main_subject. }
                OPTIONAL { ?conferences wdt:P580 ?start_time. }
                OPTIONAL { ?conferences wdt:P582 ?end_time. }
                
                OPTIONAL { ?conferences wdt:P179 ?series.
                OPTIONAL { ?series wdt:P1813 ?short_name. }
                OPTIONAL { ?series wdt:P571 ?beginnings. }
                OPTIONAL { ?series wdt:P5127 ?WikiCFP_identifier. }
                OPTIONAL { ?series wdt:P8926 ?DBLP_identifier. }}
                
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
                }'''

        output = WikidataQuery.queryWikiData(text)
        results = output['results']['bindings']

        # untangling the results in order to get a dataframe
        data_array = np.full((len(results)+1, 12), pd.NA)  # add another dimension for the columns names, 12 because there are 12 features in the query
        data_array[0, :] = np.array(['conf_label', 'title', 'country', 'location', 'main_subject', 'start_time', 'end_time', 'series_label', 'series_short_name', 'beginnings', 'WikiCFP_identifier', 'DBLP_identifier'])
        for i, result in enumerate(results):
            for name in result.keys():
                if name == 'conferencesLabel':
                    data_array[i+1, 0] = result[name]['value']
                elif name == 'title':
                    data_array[i+1, 1] = result[name]['value']
                elif name == 'countryLabel':
                    data_array[i+1, 2] = result[name]['value']
                elif name == 'locationLabel':
                    data_array[i+1, 3] = result[name]['value']
                elif name == 'main_subjectLabel':
                    data_array[i+1, 4] = result[name]['value']
                elif name == 'start_time':
                    temp = result[name]['value'].split('T')[0].split('-')
                    data_array[i+1, 5] = temp[2]+'.'+temp[1]+'.'+temp[0]  # date as DD.MM.YYYY
                elif name == 'end_time':
                    temp = result[name]['value'].split('T')[0].split('-')
                    data_array[i+1, 6] = temp[2]+'.'+temp[1]+'.'+temp[0]  # date as DD.MM.YYYY
                elif name == 'seriesLabel':
                    data_array[i+1, 7] = result[name]['value']
                elif name == 'short_name':
                    data_array[i+1, 8] = result[name]['value']
                elif name == 'beginnings':
                    data_array[i+1, 9] = result[name]['value'].split('-')[0]  # only year is taken
                elif name == 'WikiCFP_identifier':
                    data_array[i+1, 10] = result[name]['value']
                elif name == 'DBLP_identifier':
                    data_array[i+1, 11] = result[name]['value']

        # creation of the dataframe from data_array
        dataframe = pd.DataFrame(data_array[1:, :], columns=data_array[0, :])
        # also write the csv-file in the datasets folder
        if overwrite_dataset:
            WikidataQuery._write_csv_to_datasets(dataframe, 'wikidata_conf_data')
        else:
            pass

        return dataframe

    @staticmethod
    def _how_many_proceedings():
        """
        How many entries exist in Wikidata that have the property: instance of 'proceedings' (Q1143604)
        """
        text = '''
                SELECT (COUNT (?proceeding) AS ?count)
                WHERE {?proceeding wdt:P31 wd:Q1143604.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }'''
        output = WikidataQuery.queryWikiData(text)
        result = output['results']['bindings'][0]['count']['value']

        return result

    @staticmethod
    def _how_many_academic_conferences():
        """
        How many entries exist in Wikidata that have the property: instance of 'academic conference' (Q2020153)
        """
        text = '''
                SELECT (COUNT (?conferences) AS ?count)
                WHERE {?conferences wdt:P31 wd:Q2020153.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }'''
        output = WikidataQuery.queryWikiData(text)
        result = output['results']['bindings'][0]['count']['value']

        return result
    
    @staticmethod
    def _write_json_to_results(data: json, name_of_file: str) -> None:
        if name_of_file.endswith('.json'):
            raise ValueError("Just name the file without the datatype (\'.json\').")
        full_file_name = name_of_file+".json"
        path_to_file = WikidataQuery.path_to_results / full_file_name

        with open(path_to_file, 'w') as f:
                f.write(data)

    @staticmethod
    def _write_csv_to_datasets(dataframe: pd.DataFrame, name_of_file: str) -> None:
        if name_of_file.endswith('.csv'):
            raise ValueError("Just name the file without the datatype (\'.csv\').")
        dataframe.to_csv(WikidataQuery.path_to_datasets / name_of_file+'.csv')


if __name__ == "__main__":
    cre = WikidataQuery.assess_wikidata(write_to_json=True)
    print(cre)
