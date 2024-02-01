from openai import OpenAI
import polars as pl

class NLP:

    def conferenceNLP(conference,user_key, temperature=0, model="gpt-3.5-turbo"):
        client = OpenAI(api_key=user_key)
        MODEL = model
        query="Please perform NLP on the following prompt and export the entities with their type as a JSON file with the categories: title, abbreviation, date, year, location. " +conference + ". If a category can not be filled, fill it with 'not available'."

        response=client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": query}],
            temperature=temperature
        )
        return(response.choices[0].message.content.strip())
    
    def open_ai_semantification(df,user_key,dataset_name= 'Wikidata',max_entries=0, temperature=0, model="gpt-3.5-turbo"):
        data_string=""
        #define the amount of rows we want to semantify
        if max_entries>0:
            entries_count=min(len(df),max_entries)
        else:
            entries_count=len(df)
        #convert dataframe into string
        for i in range(entries_count):
            data_string+=str(df[i].cast(pl.String).to_dict(as_series=False))
        client = OpenAI(api_key=user_key)
        MODEL = model
        #default part for query
        query="""
        Please convert the following"""+entries_count+"""dictionaries into a JSON file with the conference signature elements: 
        -full_title: The full title of the event, often indicating the scope and subject.
        -short_name: The short name of the conference, often in uppercase.
        -ordinal: The instance number of the event, like 18th or 1st. 
        -part_of_series: The overlying conference-series, often a substring of full_title.
        -city_name: The year in which the conference takes place.
        -year: The year in which the conference takes place. 
        -start_time: The start date of the conference.
        -end_time: The end date of the conference.
        Valid answers for e.g. the query 
        """
        #individual part for each dataset type
        if dataset_name == 'Wikidata':
            query+= '''
            {'conf_label': ['Advances in Web Based Learning - ICWL 2007, 6th International Conference, Edinburgh, UK, August 15-17, 2007'], 'title': ['Advances in Web Based Learning - ICWL 2007, 6th International Conference'], 'country': ['United Kingdom'], 'location': ['Edinburgh'], 'main_subject': [None], 'start_time': ['15.08.2007'], 'end_time': ['17.08.2007'], 'series_label': ['International Conference on Advances in Web-Based Learning']}
             would look like
            full_title: "Advances in Web Based Learning - ICWL 2007, 6th International Conference"
            short_name: "ICWL 2007"
            ordinal: 6th
            part_of_series: "International Conference on Advances in Web-Based Learning"
            city_name: "Edinburgh"
            year: "2007"
            start_time: "15.08.2007"
            end_time: "17.08.2007"
            '''
        elif dataset_name == 'proceedings.com':
            query+='''
            {'Conference Title': ['AMERICAN COLLEGE OF VETERINARY PATHOLOGISTS. ANNUAL MEETING. 63RD 2012. (AND 47TH ANNUAL MEETING OF THE AMERICAN SOCIETY FOR VETERINARY CLINICAL PATHOLOGY)'], 'Book Title': ['63rd Annual Meeting of the American College of Veterinary Pathologists and the 47th Annual Meeting of the American Society of Veterinary Clinical Pathology 2012'], 'Series': [None], 'Description': ['Held 1-5 December 2012, Seattle, Washington, USA. '], 'Mtg Year': ['2012']} 
            would look like
            full_title: "AMERICAN COLLEGE OF VETERINARY PATHOLOGISTS. ANNUAL MEETING."
            short_name: null
            ordinal: 63rd
            part_of_series: "AMERICAN COLLEGE OF VETERINARY PATHOLOGISTS."
            city_name: "Seattle"
            year: "2012"
            start_time: "1.12.2012"
            end_time: "5.12.2012"
            '''
        #individual part for given request
        query+="perform the conversion on the following dictionary: "+data_string
        response=client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": query}],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    
    def semantifier(conferences: pl.DataFrame,user_key:str,dataset_name= 'Wikidata',max_entries=0, temperature=0, model="gpt-3.5-turbo"):
        #disambiguate the different datasets and filter the desired columns
        if dataset_name == 'Wikidata':
            df= conferences.select("conf_label","title","country","location","main_subject","start_time","end_time","series_label")
        elif dataset_name == 'proceedings.com':
            df= conferences.select("Conference Title","Book Title","Series","Description","Mtg Year")
        #semantify with openai
        data=NLP.open_ai_semantification(df,user_key,dataset_name,max_entries,temperature,model)
        return data

        
