import pandas as pd
pd.options.mode.chained_assignment = None
from transformers import BertTokenizer, BertModel
import torch

# Read .csv file
csv_file_path = '' # Edit
df = pd.read_csv(csv_file_path)

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Region of interest
# Tokenize and get BERT embeddings for conference names
def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

df['conference_embedding'] = df['name'].apply(get_bert_embeddings)
# #df2['conference_embedding'] = df2['name'].apply(get_bert_embeddings)
# #df2

# Is a speedup 
# def get_bert_embeddings(text):
#     inputs = tokenizer(text, return_tensors='pt', truncation=True)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

# df['conference_embedding'] = df['name'].apply(get_bert_embeddings)

df.head()

# Concept to calculate the similarity between conference names and proceedings
from sklearn.metrics.pairwise import cosine_similarity
# Reference embeddings should also be calculated beforehand!
# df['similarity'] = df.apply(lambda row: cosine_similarity([row['conference_embedding']], [row['proceeding_embedding']])[0][0], axis=1)
