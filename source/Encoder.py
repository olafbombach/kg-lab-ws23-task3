from source.HelperFunctions import find_root_directory
from transformers import BertTokenizer, BertModel
#from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from pathlib import Path

class Encoder:
    """
    Creates an Encoding based on a dictionary. 
    Can create the encoding using BERT or Glove.
    """
    # keywords that are redundant for the encoding
    REDUNDANT_STRINGS = ['ieee', 'iop', 'ieee/acm', 'edp', 'elsevier', 'spie', 
                         'annual', 'yearly', 'meeting', 'symposium', 'workshop', 
                         'conference', 'proceeding', 'proceedings', 'or', 
                         'and', '&', 'of', 'on', 'at', 'about']

    def __init__(self, dict_file: dict, technique: str):

        assert technique in ['bert', 'glove'], "Please make sure to use a viable encoding."

        self.dict_data = dict_file
        self.technique = technique
        self.glove_embeddings = None
        if self.technique == "glove":
            self.glove_embeddings = Encoder.load_glove_embeddings(self)

    def load_glove_embeddings(self, file_to_glove_dir: Path = find_root_directory() / "datasets" / "glove") -> dict:
        """
        Loads the necessary embedding to create encodings with Glove.
        """
        txt_file = file_to_glove_dir / "glove.6B.50d.txt"
        assert txt_file.exists(), "Please make sure, that the embedding of Glove is already downloaded locally!"

        glove_embeddings = dict()
        with open(txt_file, 'r', encoding='utf8') as file:
            for line in file:
                values = line.split()
                word = values[0]
                vector = np.array(values[1:], dtype='float32')
                glove_embeddings[word] = vector
        return glove_embeddings

    def get_bert_embedding(self, value: str):
        """
        Method to get BERT embedding for a specific value.
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
        
    def get_glove_word_embedding(self, value: str): 
        """
        Method to get Glove embedding for a specific value.
        """
        if not self.glove_embeddings:
            raise ValueError("GloVe word embeddings not loaded, call load_embeddings")
        else:
            return self.glove_embeddings.get(value, None)
    

    def get_glove_encoding(self, **kwargs):
        """
        Specify the attributs you want to include in your encoding as boolean kwargs.
        Possible values: 
        full_title, short_name, ordinal, part_of_series, country_name,
        country_short, city_name, year, start_time, end_time.
        """
        assert set(kwargs.keys()) <= {"full_title", "short_name", "ordinal", "part_of_series", "country_name", "country_short", "city_name", "year", "start_time", "end_time"}, \
        "You chose a wrong keyword argument!"

        # get string
        text_to_evaluate = ""
        for name, val in kwargs.items():
            text_to_evaluate = Encoder.add_string(self, 
                                                  current_string=text_to_evaluate, 
                                                  name_of_attribute=name, 
                                                  value_of_attribute=val)
        
        text_to_evaluate = text_to_evaluate.strip()
        words = text_to_evaluate.split()
        embeddings = [self.get_glove_word_embedding(word) for word in words]
        embeddings = [emb for emb in embeddings if emb is not None]
        
        if not embeddings:
            return None
        else:
            return np.mean(embeddings, axis=0)
    
    def get_bert_encoding(self, **kwargs):
        """
        Specify the attributs you want to include in your encoding as boolean kwargs.
        Possible values: 
        full_title, short_name, ordinal, part_of_series, country_name,
        country_short, city_name, year, start_time, end_time.
        """
        assert set(kwargs.keys()) <= {"full_title", "short_name", "ordinal", "part_of_series", "country_name", "country_short", "city_name", "year", "start_time", "end_time"}, \
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
    
    def add_string(self, current_string: str, name_of_attribute: str, value_of_attribute: bool) -> str:
        """
        Get the string that is to evaluate.
        This method is iterated over all keyword arguments.
        
        Each keyword is sorted based on the first letter of the strings.
        Further some redundant strings (fillwords) are sorted out.
        """        
        if value_of_attribute:    
            if self.dict_data[name_of_attribute] is not None:
                current_addition = self.dict_data[name_of_attribute].lower()
                # separation and alphabetically sorting
                sep_strings_as_lst = Encoder._separate_into_list(current_addition)
                sorted_list = sorted(sep_strings_as_lst)
                # sorting out redundant_strings
                final_lst = [string for string in sorted_list if string not in Encoder.REDUNDANT_STRINGS]
                final_add = ' '.join(final_lst)
        
                current_string += " " + final_add
            else:
                pass
        return current_string.strip()  
    
    @staticmethod
    def _separate_into_list(addition: str):
        """
        Separate string into list.
        Separation first based on \" \". 
        Afterwards we check if there are \"/\", \",\" or \".\" inside the string.
        In this case delete these characters and try to separate into further strings.
        In the end it checks if the string is longer than 1 letter.
        """
        final = []
        start_lst = addition.split()
        for word in start_lst:
            ls_of_word = []
            for char in [",", ".", "/"]:
                if len(ls_of_word) == 0:
                    if char in word:
                        ls_of_word = word.split(char)
                    else:
                        pass              
                else:
                    for substring in ls_of_word:
                        if char in substring:
                            further_substrings = substring.split(char)
                            ls_of_word.remove(substring)
                            ls_of_word.extend(further_substrings)
                        else:
                            pass
            if len(ls_of_word) > 0:
                ls_of_word = [subs for subs in ls_of_word if len(subs) > 1]
                final.extend(ls_of_word)
            else:
                if len(word) > 1:
                    final.append(word)
        return final

