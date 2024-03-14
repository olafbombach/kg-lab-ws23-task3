from typing import Union
import logging
import os
from pathlib import Path

from openai import OpenAI
import polars as pl
import json

http_logger = logging.getLogger("http")
http_logger.setLevel(logging.WARNING)

class Semantifier:

    def __init__(self, dataset_name: str, openai_key: str = None, temperature: float=0, model: str="gpt-3.5-turbo"):
        self.dataset_name = dataset_name
        self.temperature = temperature
        self.model = model
        
        # get openai key
        if openai_key:
            self.key = openai_key
        else:
            # Load the API key from the environment or a JSON file
            openai_key = os.getenv("OPENAI_API_KEY")
            json_file = Path.home() / ".openai" / "openai_api_key.json"

            if openai_key is None and json_file.resolve().is_file():
                with open(json_file, "r") as file:
                    data = json.load(file)
                    openai_key = data.get("OPENAI_API_KEY")

        if openai_key is None:
            raise ValueError(
                "No OpenAI API key found. Please set the 'OPENAI_API_KEY "
                "environment variable or "
                "store it in `~/.openai/openai_api_key.json`.")
        # set the global api key
        self.key = openai_key


    def conferenceNLP(self, conference):
        client = OpenAI(api_key=self.key)
        MODEL = self.model
        query = "Please perform NLP on the following prompt and export the entities with their type as a JSON file with the categories: title, abbreviation, date, year, location. " +conference + ". If a category can not be filled, fill it with 'not available'."

        response = client.chat.completions.create(model = MODEL,
                                                  messages = [{"role": "user", "content": query}],
                                                  temperature = self.temperature)
        
        return(response.choices[0].message.content.strip())
    
    def open_ai_semantification(self, 
                                data: Union[dict, pl.DataFrame], 
                                max_entries: int = 0):
        data_string=""
        # define the amount of rows we want to semantify
        if self.dataset_name == 'Wikidata':
            entries_count = 1
            data_string = str(data)
            """if max_entries > 0:
                entries_count = min(len(data), max_entries)
            else:
                entries_count = len(data)
                # convert dataframe into string
            for i in range(entries_count):
                data_string += str(data[i].to_dict(as_series=False))"""
        elif self.dataset_name == 'proceedings.com':
            # this method should be optimized
            entries_count = 1
            data_string = str(data)        

        client = OpenAI(api_key=self.key)
        MODEL = self.model
        # default part for query
        query = """Please convert the following""" + \
        str(entries_count) + \
        """dictionaries into a json file with the conference signature elements: 
        -full_title: The full title of the event, often indicating the scope and subject. Please make sure to delete any ordinals or shortnames here. If there is a short_name provided, you can try to validate the full_title by checking if the letters in the short title add up to the first letters of the full_title. 
        -short_name: The short name of the conference, often in uppercases. If provided closely in the string, you can also add the year of the conference in YYYY format. 
        -ordinal: The instance number of the event, like 18th or 1st. Sometimes this is also written as first, second, etc.
        -part_of_series: The overlying conference-series, often a substring of full_title.
        -country_name: The country in which the conference takes place.
        -country_short: The unique identifier with respect to the country that is found. Give this identifier using a 2 digit ISO 3166-1 alpha-2 code.
        -city_name: Give the city with it's english label.
        -year: Give the year of the conference as a 4 digit number.
        -start_time: The start date of the conference in ISO date format.
        -end_time: The end date of the conference in ISO date format.
        Valid answers for e.g. the query 
        """
        #individual part for each dataset type
        if self.dataset_name == 'Wikidata':
            query += """
            {'conf_label': ['Advances in Web Based Learning - ICWL 2007, 6th International Conference, Edinburgh, UK, August 15-17, 2007'], 'title': ['Advances in Web Based Learning - ICWL 2007, 6th International Conference'], 'country': ['United Kingdom'], 'location': ['Edinburgh'], 'main_subject': [None], 'start_time': ['15.08.2007'], 'end_time': ['17.08.2007'], 'series_label': ['International Conference on Advances in Web-Based Learning']}
             would look like
            {full_title: 'International Conference of Advances in Web Based Learning',
            short_name: 'ICWL 2007',
            ordinal: '6th',
            part_of_series: 'International Conference on Advances in Web-Based Learning',
            country_name: 'United Kingdom',
            country_identifier: 'UK',
            city_name: 'Edinburgh',
            year: '2007',
            start_time: '2007-08-15',
            end_time: '2007-08-17'}
            """
        elif self.dataset_name == 'proceedings.com':
            query += """
            {'Conference Title': 'AMERICAN COLLEGE OF VETERINARY PATHOLOGISTS. ANNUAL MEETING. 65TH 2014. (AND 49TH ANNUAL MEETING OF THE AMERICAN SOCIETY FOR VETERINARY CLINICAL PATHOLOGY, IN PARTNERSHIP WITH ASIP)', 'Book Title': '65th Annual Meeting of the American College of Veterinary Pathologists and the 49th Annual Meeting of the American Society of Veterinary Clinical Pathology (ACVP & ASVCP 2014)', 'Series': None, 'Description': 'Held 8-12 November 2014, Atlanta, Georgia, USA. In Partnership with ASIP.', 'Mtg Year': '2014'} 
            would look like
            {full_title: 'Annual Meeting American College of Veterinary Pathologists',
            short_name: 'None',
            ordinal: '63rd',
            part_of_series: 'American College of Veterinary Pathologists',
            country_name: 'USA',
            country_identifier: 'US',
            city_name: 'Seattle',
            year: '2012',
            start_time: '2012-12-01',
            end_time: '2012-12-05'}
            """
        # individual part for given request
        query += "perform the conversion on the following dictionary: " + data_string + ". If a signature element is not given in the query, fill the corresponding element with \"None\"."
        response = client.chat.completions.create(model=MODEL,
                                                messages=[{"role": "user", "content": query}],
                                                temperature=self.temperature)
        try:
            dict_file = json.loads(response.choices[0].message.content.strip())

        except json.decoder.JSONDecodeError:
            new_query = query + " Please assure that your response is a proper JSON file. The means that each key and each value have to be in quotation marks."
            print("1")
            altered_response = client.chat.completions.create(model=MODEL,
                                                messages=[{"role": "user", "content": new_query}],
                                                temperature=self.temperature)
            print(altered_response.choices[0].message.content.strip())
            dict_file = json.loads(altered_response.choices[0].message.content.strip())

        return dict_file
    
    def semantifier(self, 
                    conferences: Union[dict, pl.DataFrame],
                    max_entries: int  = 0):
        # disambiguate the different datasets and filter the desired columns
        if self.dataset_name == 'Wikidata':
            # datatype: polars data frame
            df = {key: conferences[key] for key in ("conf_label","title","country","location","main_subject","start_time","end_time","series_label")}
            #df = conferences.select("conf_label","title","country","location","main_subject","start_time","end_time","series_label")
        elif self.dataset_name == 'proceedings.com':
            # datatype: dictionary
            # df= conferences.select("Conference Title","Book Title","Series","Description","Mtg Year")
            df = {key: conferences[key] for key in ("Conference Title","Book Title","Series","Description","Mtg Year")}
        # semantify with openai
        data = Semantifier.open_ai_semantification(self,
                                                   df, 
                                                   max_entries)
        return data

        
