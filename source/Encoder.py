import json
from transformers import BertTokenizer, BertModel
#from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial

class Encoder:

    # # Read JSON file and return it
    # def read_json(self, file_path):
    #     with open(file_path, 'r') as file:
    #           conference_data = json.load(file)
    #     return conference_data
    def __init__(self, dict_file: dict):
        self.dict_data = dict_file
        # TODO create a downloader class that gets the required datasets from their source, unpack in the working directory
        # the path should then point to the said directory. 
        """glove_path = "/home/efeboz/Desktop/glove.6B/glove.6B.50d.txt"
        self.glove_embeddings = self.load_glove_embeddings(glove_path)"""

    # Read GloVe dataset
    def load_glove_embeddings(self, file_path):
        glove_embeddings = {}
        with open(file_path, 'r') as file:
            for line in file:
                values = line.split()
                word = values[0]
                vector = np.array(values[1:], dtype='float32')
                glove_embeddings[word] = vector
        self.glove_embeddings = glove_embeddings
        return glove_embeddings

    def get_bert_embedding(self, value):
        """
        Load pre-trained BERT model and tokenizer.

        Function to get BERT embedding for a value.
        Only to make a prediction, no actual training.
        """
        # Load pre-trained BERT model and tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True).eval()
        tokens = tokenizer(value, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**tokens)
            # last_hidden_state accesses the last layer of hidden states
            # mean across the tokens for each sequence to get a fixed size representation
            # squeeze() for 1 dimensional tensor
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    
        
    # Get embedding for word from GloVe dataset
    def get_glove_word_embedding(self, word): 
        if not self.glove_embeddings:
            raise ValueError("GloVe word embeddings not loaded, call load_embeddings")
        return self.glove_embeddings.get(word, None)
    
    # Apply for a set of string
    # entry_no: integer value for selecting the JSON element for computation
    # optional parameters title, abbreviation, date, year, location of type boolean. Passing these parameters indicate which elements are going to be calculated
    # TODO empty string "" has also an embedding value, find a solution to not calculate it
    def get_glove_encoding(self, entry_no: int, title: bool=None, abbreviation: bool=None, date: bool=None, year: bool=None, location: bool=None):
        conference_data = self.dict_file
        if not self.glove_embeddings:
            raise ValueError("GloVe word embeddings not loaded, call load_embeddings")
        conference_title = conference_data[entry_no]['title'] if conference_data[entry_no]['title'] != "not available" else ""
        conference_abbreviation = conference_data[entry_no]['abbreviation'] if conference_data[entry_no]['abbreviation'] != "not available" else ""
        conference_date = conference_data[entry_no]['date'] if conference_data[entry_no]['date'] != "not available" else ""
        conference_year = conference_data[entry_no]['year'] if conference_data[entry_no]['year'] != "not available" else ""
        conference_location = conference_data[entry_no]['location'] if conference_data[entry_no]['location'] != "not available" else ""
        text_to_evaluate = ""
        if title is True:
            text_to_evaluate += conference_title
        if abbreviation is True:
            text_to_evaluate += " " + conference_abbreviation
        if date is True:
            text_to_evaluate += " " + conference_date
        if year is True:
            text_to_evaluate += " " + conference_year
        if location is True:
            text_to_evaluate += " " + conference_location
        text_to_evaluate.replace(" ", " ").strip()
        words = text_to_evaluate.split()
        embeddings = [self.get_glove_word_embedding(word) for word in words]
        embeddings = [emb for emb in embeddings if emb is not None]
        if not embeddings:
            return None
        return np.mean(embeddings, axis=0)
        #return self.glove_embeddings.get(word, None)
    
    def add_string(self, current_string: str, name_of_attribute: str, value_of_attribute: bool) -> str:
        """
        Get the string that is to evaluate.
        This method is iterated over all chosen keyword arguments.
        """
        if value_of_attribute: 
            if self.dict_data[name_of_attribute] is not None:
                current_string += " " + self.dict_data[name_of_attribute]
            else:
                pass
        return current_string

    # entry_no: integer value for selecting the JSON element for computation
    # optional parameters title, abbreviation, date, year, location of type boolean. Passing these parameters indicate which elements are going to be calculated
    # TODO empty string "" has also an embedding value, find a solution to not calculate it
    def get_bert_encoding(self, **kwargs):
        """
        Specify the attributs you want to include in your encoding as boolean kwargs.
        Possible values: 
        full_title, short_name, ordinal, part_of_series, country_name,
        country_identifier, city_name, year, start_time, end_time.
        """
        assert set(kwargs.keys()) <= {"full_title", "short_name", "ordinal", "part_of_series", "country_name", "country_identifier", "city_name", "year", "start_time", "end_time"}, \
        "You chose a wrong keyword argument!"
        
        # get string
        text_to_evaluate = ""
        for name, val in kwargs.items():
            text_to_evaluate = Encoder.add_string(self, 
                                                  current_string=text_to_evaluate, 
                                                  name_of_attribute=name, 
                                                  value_of_attribute=val)
        
        text_to_evaluate = text_to_evaluate.strip()
        return self.get_bert_embedding(text_to_evaluate)
    
    def get_cosine_similarity(self, embedding1, embedding2):
        embedding1 = np.array(embedding1).reshape(1, -1)
        embedding2 = np.array(embedding2).reshape(1, -1)
        similarity = cosine_similarity(embedding1, embedding2)
        return similarity[0][0]
    
    def get_bert_euclidean(self, embedding1, embedding2):
        similarity = spatial.distance.euclidean(embedding1, embedding2)
        return similarity
    


# #Test if the class works
# Sample JSON
# json = [
# 	{
#   		"title": "FIELD-PROGRAMMABLE TECHNOLOGY",
#   		"abbreviation": "FPT 2010",
#   		"date": "not available",
#   		"year": "2010",
#   		"location": "not available"
# 	},
# 	{
#   		"title": "SEMICONDUCTOR CONFERENCE",
#   		"abbreviation": "CAS",
#   		"date": "2011",
#   		"year": "2011",
#   		"location": "not available"
# 	},
# 	{
#   		"title": "ENVIRONMENTAL SCIENCE AND DEVELOPMENT",
#   		"abbreviation": "ICESD",
#   		"date": "9TH",
#   		"year": "2018",
#   		"location": "not available"
# 	}
# ]
# #Bert
# instance = Encoder(json)
# json_path = "/home/efeboz/Desktop/OpenAI_output_example.json" # Now uncessery with the introduction of __init__
# data = instance.read_json(json_path) # Also not necessery
# bert1 = instance.get_bert_encoding(0, year=True)
# bert2 = instance.get_bert_encoding(1, year=True)
# bert3 = instance.get_cosine_similarity(bert1, bert2)
# bert4 = instance.get_bert_euclidean(bert1,bert2)
# print(bert4)

# #GloVe
# glove_path = "/home/efeboz/Desktop/glove.6B/glove.6B.50d.txt"
# glove_embeddings = instance.load_glove_embeddings(glove_path)
# glove1 = instance.get_glove_encoding(0, year=True)
# glove2 = instance.get_glove_encoding(1, year=True)
# glove3 = instance.get_cosine_similarity(glove1, glove2)
# glove4 = instance.get_bert_euclidean(glove1, glove2)
# print(glove4)

