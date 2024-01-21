import json
from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class NlpEncoder:

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
              conference_data = json.load(file)
        return conference_data

    # json_file_path = "/home/efeboz/Desktop/OpenAI_output_example.json"
    # with open(json_file_path, 'r') as file:
    #         conference_data = json.load(file)

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
    
    def get_embedding_list(self, conference_data):
         embedding_list = []
         for conference in conference_data:
            concatenated_values = ' '.join(value if value != "not available" else "" for value in conference.values())
            embeddings = self.get_bert_embedding(concatenated_values)
            embedding_list.append(embeddings)
            conference["embedding"] = embeddings
         return embedding_list
    
    def get_cosine_similarity(self, embedding1, embedding2):
        embedding1 = np.array(embedding1).reshape(1, -1)
        embedding2 = np.array(embedding2).reshape(1, -1)
        similarity = cosine_similarity(embedding1, embedding2)
        return similarity[0][0]
              
# Test if it works
# instance = NlpEncoder()
# file_path = "/home/efeboz/Desktop/OpenAI_output_example.json"
# data = instance.read_json(file_path)
# test1 = instance.get_embedding_list(data)
# test2 = instance.get_cosine_similarity(test1[0],test1[1])
# print(test1)
# print(test2) 
