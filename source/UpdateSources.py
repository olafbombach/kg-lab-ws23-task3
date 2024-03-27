
from typing import Union
from datetime import datetime
import json
import os
from os.path import isfile, join
import polars as pl

from bs4 import BeautifulSoup
from urllib.request import urlretrieve, urlopen
from lodstorage.sparql import SPARQL

from source.HelperFunctions import find_root_directory


class WikidataQuery(object):
    """
        An operator that enables to query from wikidata.
        It comes with some additional methods that can display the current status of wikidata conference entries.
        It further creates the dataset used for the data synchronization.
    """

    query = SPARQL("https://query.wikidata.org/sparql")
    root_dir = find_root_directory()
    path_to_results = root_dir / "results"
    path_to_datasets = root_dir / "datasets" / "wikidata"

    @staticmethod
    def queryWikiData(input_text: str):
        """
        The method to query using SPARQLWrapper.
        """
        result = WikidataQuery.query.rawQuery(input_text)
        return result

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
    def getWDIdfromLabel(name: str):
        """
        Find the entry in Wikidata that has a certain label.
        Input: label (type: str)
        Returns: The QID of the item or None if it does not exist.
        In case of a timeout or a false label, None is returned.
        """
        try: 
            s = name.lower()
            text = """
                    SELECT DISTINCT ?item ?label
                    WHERE
                    {
                    SERVICE wikibase:mwapi
                        {
                        bd:serviceParam wikibase:endpoint "www.wikidata.org";
                                        wikibase:api "Generator";
                                        mwapi:generator "search";
                                        mwapi:gsrsearch "inlabel:"""+s+"""\"@en;
                                        mwapi:gsrlimit "max".
                        ?item wikibase:apiOutputItem mwapi:title.
                    }
                    ?item rdfs:label ?label. FILTER( LANG(?label)="en" )
                     ?item rdfs:label ?label. FILTER(CONTAINS(LCASE(?label), \""""+s+"""\") )

                    }
                    order by strlen(str(?label)) desc(?item)
                    LIMIT 1
                   """
            
            result = WikidataQuery.queryWikiData(text)
            WDresults= result.getValues("item")

            if len(WDresults) > 0:
                for w in WDresults:
                    uri = w.value
                    WDid = uri[uri.find("entity")+7:]        
            else:
                WDid = None
            return WDid
        
        except Exception as e:
          print(e)
          return None   

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
    def create_wikidata_dataset(overwrite_dataset: bool = False) -> pl.DataFrame:
        """
        This method (query) gets all conferences and their information as a polars DataFrame.
        It further directly overwrites the dataset-file for wikidata.
        """
        text = '''
                SELECT ?conferences ?conferencesLabel ?title ?countryLabel ?short_name ?country ?locationLabel 
                ?location ?main_subjectLabel ?start_time ?end_time ?seriesLabel 
                ?ser_short_name ?beginnings ?WikiCFP_identifier ?DBLP_identifier
                
                WHERE {?conferences wdt:P31 wd:Q2020153.                
                OPTIONAL { ?conferences wdt:P1476 ?title. }
                OPTIONAL { ?conferences wdt:P1813 ?short_name. }
                OPTIONAL { ?conferences wdt:P17 ?country. }
                OPTIONAL { ?conferences wdt:P276 ?location. }
                OPTIONAL { ?conferences wdt:P921 ?main_subject. }
                OPTIONAL { ?conferences wdt:P580 ?start_time. }
                OPTIONAL { ?conferences wdt:P582 ?end_time. }
                OPTIONAL { ?conferences wdt:P179 ?series.
                OPTIONAL { ?series wdt:P1813 ?ser_short_name. }
                OPTIONAL { ?series wdt:P5127 ?WikiCFP_identifier. }
                OPTIONAL { ?series wdt:P8926 ?DBLP_identifier. }}
                
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
                }'''
        
        lod = WikidataQuery.query.queryAsListOfDicts(text)
        result = []
        for entry in lod:
            conf_label = entry.get("conferencesLabel", None)
            conf_qid = entry.get("conferences", None)
            title = entry.get("title", None)
            short_name = entry.get("short_name", None)
            country = entry.get("countryLabel", None)
            country_qid = entry.get("country", None)
            location = entry.get("locationLabel", None)
            location_qid = entry.get("location", None)
            main_subject = entry.get("main_subjectLabel", None)
            start_time = entry.get("start_time", None)
            end_time = entry.get("end_time", None)
            series_label = entry.get("seriesLabel", None)
            series_short_name = entry.get("ser_short_name", None)
            WikiCFP_identifier = entry.get("WikiCFP_identifier", None)
            DBLP_identifier = entry.get("DBLP_identifier", None)
            if conf_qid:
                conf_qid = conf_qid.replace("http://www.wikidata.org/entity/", "")
            if country_qid:
                country_qid = country_qid.replace("http://www.wikidata.org/entity/", "")
            if location_qid:
                location_qid = location_qid.replace("http://www.wikidata.org/entity/", "")

            entry_list = [conf_label, conf_qid, title, short_name, country, country_qid, location, location_qid, 
                          main_subject, start_time, end_time, series_label, series_short_name, 
                          WikiCFP_identifier, DBLP_identifier]
            
            col_for_df = ['conf_label', 'conf_qid', 'title', 'short_name', 'country', 'country_qid', 
                          'location', 'location_qid', 'main_subject', 'start_time', 'end_time', 'series_label', 
                          'series_short_name', 'WikiCFP_identifier', 'DBLP_identifier']
            result.append(entry_list)
        
        df = pl.DataFrame(result, schema=col_for_df)
        df = WikidataQuery.preprocess_dataframe(df)

        # also write the csv-file in the datasets folder
        if overwrite_dataset:
            WikidataQuery._write_csv_to_datasets(df, 'wikidata_conf_data')
        else:
            pass

        return df

    @staticmethod
    def _how_many_proceedings():
        """
        How many entries exist in Wikidata 
        that have the property: instance of 'proceedings' (Q1143604)
        """
        text = '''
                SELECT (COUNT (?proceeding) AS ?count)
                WHERE {?proceeding wdt:P31 wd:Q1143604.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }'''
        output = WikidataQuery.queryWikiData(text)
        result = output.bindings[0]['count'].value

        return result

    @staticmethod
    def _how_many_academic_conferences():
        """
        How many entries exist in Wikidata 
        that have the property: instance of 'academic conference' (Q2020153)
        """
        text = '''
                SELECT (COUNT (?conferences) AS ?count)
                WHERE {?conferences wdt:P31 wd:Q2020153.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }'''
        output = WikidataQuery.queryWikiData(text)
        result = output.bindings[0]['count'].value

        return result
    
    @staticmethod
    def preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        """
        Returns the preprocessed dataframe, 
        deleting all duplicates by concatinating all found strings.
        """
        df = df.group_by('conf_qid').agg(pl.all().unique().map_elements(WikidataQuery.concatenate_lst))

        return df

    @staticmethod
    def concatenate_lst(lst: Union[list,datetime,None]) -> str:
        """
        Needed for the preprocessing of the Dataframe.
        Given a unique list returns a concatenated string.
        """
        str_lst = [element for element in lst if element is not None]
        str_lst = [element if not isinstance(element, datetime) else element.strftime("%Y-%m-%d %H:%M:%S") for element in str_lst]
        return " / ".join(str_lst)        
    
    @staticmethod
    def _write_json_to_results(data: object, name_of_file: str) -> None:
        if name_of_file.endswith('.json'):
            raise ValueError("Just name the file without the datatype (\'.json\').")
        full_file_name = name_of_file+".json"
        path_to_file = WikidataQuery.path_to_results / full_file_name

        with open(path_to_file, 'w') as f:
                f.write(data)

    @staticmethod
    def _write_csv_to_datasets(dataframe: pl.DataFrame, name_of_file: str) -> None:
        if name_of_file.endswith('.csv'):
            raise ValueError("Just name the file without the datatype (\'.csv\').")
        full_file_name = name_of_file+'.csv'
        path_to_file = WikidataQuery.path_to_datasets / full_file_name
        dataframe.write_csv(path_to_file, include_header=True, separator=';')


class ProceedingsUpdater:
    """
    An object that is able to scrape the current Proceedings.com excel file.
    """

    def updateProceedings():
        """
        The method to update the Proceedings.com excel file.
        """
        url = "https://www.proceedings.com/catalog.html"
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all('table')
        #Search for correct datarow
        lineFound=False
        offset=4
        #Search for corresponding new dataset
        for row in tables[0]:
            if (lineFound):
                offset-=1
                if offset==0:
                    datarow=row
                    break
            if (str(type(row))=="<class 'bs4.element.Comment'>"):
                if ("Cumulative" in row):
                    lineFound=True
        #Search for name of latest dataset
        for string in datarow.strings:
            if ('.xlsx' in string):
                newfile=string
        #Search for name of current dataset
        path=find_root_directory()
        path_to_dataset = path / "datasets" / "proceedings.com"
        oldfile=""
        files = [f for f in os.listdir(path_to_dataset) if isfile(join(path_to_dataset, f))]
        for file in files:
            if ('.xlsx' in file):
                oldfile=file
        #Update file
        if (newfile != oldfile):
            datalink=""
            for item in datarow.children:
                for data in item:
                    if (str(type(data))=="<class 'bs4.element.Tag'>"):
                        if (data.attrs['href']!=""):
                            datalink=data.attrs['href']        
            fulldatalink='https://www.proceedings.com'+datalink[2:]
            # download new file
            path, headers = urlretrieve(fulldatalink, path_to_dataset / newfile)
            if oldfile!="":
                os.remove(path_to_dataset / oldfile)
            else:
                pass
        else:
            pass

