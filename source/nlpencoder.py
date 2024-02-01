import json
from transformers import BertTokenizer, BertModel
#from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial

class Encoder:

    # Read JSON file and return it
    def read_json(self, file_path):
        with open(file_path, 'r') as file:
              conference_data = json.load(file)
        return conference_data

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

    # Function to get BERT embeddings for a value
    # Only to make a prediction, no actual training
    def get_bert_embedding(self, value):
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
    def get_glove_encoding(self, conference_data, entry_no: int, title: bool=None, abbreviation: bool=None, date: bool=None, year: bool=None, location: bool=None):
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
    

    # entry_no: integer value for selecting the JSON element for computation
    # optional parameters title, abbreviation, date, year, location of type boolean. Passing these parameters indicate which elements are going to be calculated
    # TODO empty string "" has also an embedding value, find a solution to not calculate it
    def get_bert_encoding(self, conference_data, entry_no: int, title: bool=None, abbreviation: bool=None, date: bool=None, year: bool=None, location: bool=None):
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
        return self.get_bert_embedding(text_to_evaluate)
    
    def get_cosine_similarity(self, embedding1, embedding2):
        embedding1 = np.array(embedding1).reshape(1, -1)
        embedding2 = np.array(embedding2).reshape(1, -1)
        similarity = cosine_similarity(embedding1, embedding2)
        return similarity[0][0]
    
    def get_bert_euclidean(self, embedding1, embedding2):
        similarity = spatial.distance.euclidean(embedding1, embedding2)
        return similarity
    

    # ############# Bert Training #############
    # #TODO Check if this makes sense as a whole
    # def encode_data(self, data_item):
    #     tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    #     inputs = tokenizer.encode_plus(
    #         f"{data_item['text']} {tokenizer.sep_token} {data_item['extra_info']}",
    #         add_special_tokens=True,
    #         max_length=512,
    #         return_tensors='pt',
    #         padding='max_length',
    #         truncation=True
    #     )
    #     return {
    #         'input_ids': inputs['input_ids'],
    #         'attention_mask': inputs['attention_mask'],
    #         'labels': torch.tensor(data_item['label'])
    #         }

    # def do_train(self, train_data):
    #     #tokenize and encode the training data
    #     encoded_train_data = [self.encode_data(item) for item in train_data]

    #     #define training arguments
    #     #TODO check if these make sense
    #     training_args = TrainingArguments(
    #     output_dir='./results',
    #     num_train_epochs=3,
    #     per_device_train_batch_size=16,
    #     warmup_steps=500,
    #     weight_decay=0.01,
    #     )
    #     #init Trainer
    #     trainer = Trainer(
    #     model=BertForSequenceClassification.from_pretrained('bert-base-uncased'),
    #     args=training_args,
    #     train_dataset=encoded_train_data,
    #     )
    #     #fine-tune bert model
    #     trained_bert = trainer.train()

    #     return trained_bert


#Test if the class works

#Bert
instance = Encoder()
json_path = "/home/efeboz/Desktop/OpenAI_output_example.json"
data = instance.read_json(json_path)
bert1 = instance.get_bert_encoding(data, 0, year=True)
bert2 = instance.get_bert_encoding(data, 1, year=True)
bert3 = instance.get_cosine_similarity(bert1, bert2)
bert4 = instance.get_bert_euclidean(bert1,bert2)
print(bert4)

#GloVe
glove_path = "/home/efeboz/Desktop/kg-lab-ws23-task3/datasets/glove.6B/glove.6B.50d.txt"
glove_embeddings = instance.load_glove_embeddings(glove_path)
glove1 = instance.get_glove_encoding(data, 0, year=True)
glove2 = instance.get_glove_encoding(data, 1, year=True)
glove3 = instance.get_cosine_similarity(glove1, glove2)
glove4 = instance.get_bert_euclidean(glove1, glove2)
print(glove4)


#prepare input data, text is the primary source information whereas extra_info is of secondary importance. This process can be extended arbitrarily
#label 
# train_data = [
#     #{"text": "text 1", "extra_info": "Additional information 1", "label": 0},
#     {"text": "Proceeding 1", "label": 0},
# ]