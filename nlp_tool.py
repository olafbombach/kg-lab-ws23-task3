import json
from transformers import BertTokenizer, BertModel
import torch
import numpy as np

# # Your JSON data
# conference_data = [
#     {
#         "title": "FIELD-PROGRAMMABLE TECHNOLOGY",
#         "abbreviation": "FPT 2010",
#         "date": "not available",
#         "year": "2010",
#         "location": "not available"
#     },
#     {
#         "title": "SEMICONDUCTOR CONFERENCE",
#         "abbreviation": "CAS",
#         "date": "2011",
#         "year": "2011",
#         "location": "not available"
#     },
#     {
#         "title": "ENVIRONMENTAL SCIENCE AND DEVELOPMENT",
#         "abbreviation": "ICESD",
#         "date": "9TH",
#         "year": "2018",
#         "location": "not available"
#     }
# ]

#conference_data = json.load("/home/efeboz/Desktop/OpenAI_output_example.json")
json_file_path = "/home/efeboz/Desktop/OpenAI_output_example.json"
with open(json_file_path, 'r') as file:
        conference_data = json.load(file)

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True).eval()

# Function to get BERT embeddings for a value
# Only to make a prediction, no actual training
def get_bert_embedding(value):
    tokens = tokenizer(value, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**tokens)
        # last_hidden_state accesses the last layer of hidden states
        # mean across the tokens for each sequence to get a fixed size representation
        # squeeze() for 1 dimensional tensor
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

embedding_list = []
# Calculate embeddings for each element in JSON
# Add new key value pair for the corresponding element
for conference in conference_data:
    concatenated_values = ' '.join(value if value != "not available" else "" for value in conference.values())
    embeddings = get_bert_embedding(concatenated_values)
    embedding_list.append(embeddings)
    conference["embedding"] = embeddings
    #print(concatenated_values)
    # #print(conference)
    #print(concatenated_values)

from sklearn.metrics.pairwise import cosine_similarity
similarity_score = cosine_similarity(np.array(embedding_list[0]).reshape(1, -1), np.array(embedding_list[1]).reshape(1, -1))
#print(similarity_score[0][0])
#print("\n", conference_data)
#print(embedding_list)

#print(conference_data)
# numbers between 0-2
hallucination1 = "SEMICONDUCTOR INTERNATIONAL CONFERENCE CAS 2011 2011" #INTERNATIONAL added as deviation parameter
hallucination2 = "YEARLY ENVIRONMENTAL SCIENCE AND DEVELOPMENT ICESD 9TH 2018" #YEARLY added as deviation parameter
#hallucination2 = "9th ICESD 2018" #YEARLY added as deviation parameter
hallucination3 = "9th ICESD (2018)"

hal4 = "9th"
hal5 = "ninth"

hal4em = get_bert_embedding(hal4)
hal5em = get_bert_embedding(hal5)

hallucination1_embedding = get_bert_embedding(hallucination1)
hallucination2_embedding = get_bert_embedding(hallucination2)

hallucination3_embedding = get_bert_embedding(hallucination3)

similarity_score1 = cosine_similarity(np.array(embedding_list[1]).reshape(1, -1), np.array(hallucination1_embedding).reshape(1, -1))
similarity_score2 = cosine_similarity(np.array(embedding_list[2]).reshape(1, -1), np.array(hallucination2_embedding).reshape(1, -1))
similarity_score0 = cosine_similarity(np.array(embedding_list[0]).reshape(1, -1), np.array(embedding_list[0]).reshape(1, -1))

similarity_score3 = cosine_similarity(np.array(hallucination3_embedding).reshape(1, -1), np.array(hallucination2_embedding).reshape(1, -1))

similarity_score4 = cosine_similarity(np.array(hal4em).reshape(1, -1), np.array(hal5em).reshape(1, -1))

# print(similarity_score0[0][0])
# print(similarity_score1[0][0])
#print(similarity_score2[0][0])

#print(similarity_score3[0][0])
print(similarity_score4[0][0])


