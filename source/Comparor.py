from source.EventClass import ProceedingsEvent, ListOfEvents

from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import numpy as np

class Comparor:

    def __init__(self, pe: ProceedingsEvent, loe: ListOfEvents):
        self.pe = pe
        self.loe = loe

    def add_measure_as_attribute(self, metric: str) -> None:
        """
        Get the optimal similarity for the List of Events 
        regarding the ProceedingsEvents. Possible values for metric are 
        \"euc\" and \"cos\".
        """
        assert metric in {"cos", "euc"}, "Your method is not supported."
        
        if metric == "cos":
            for entry in self.loe.list_of_events:
                sim = Comparor.cos_similarity(self.pe.encoding, entry.encoding)
                entry.similarity = sim
        elif metric == "euc":
            for entry in self.loe.list_of_events:
                sim = Comparor.euclidean_similarity(self.pe.encoding, entry.encoding)
                entry.similarity = sim
        else:
            pass

    @staticmethod
    def cos_similarity(emb_1: np.ndarray, emb_2: np.ndarray) -> float:
        """
        Returns the cosine similarity measure between two embeddings.
        """
        emb_1 = emb_1.reshape(1,-1)
        emb_2 = emb_2.reshape(1,-1)
        sim = cosine_similarity(emb_1, emb_2)
        return sim[0][0]

    @staticmethod
    def euclidean_similarity(emb_1:np.ndarray, emb_2: np.ndarray) -> float:
        """
        Returns the euclidean distance between two embeddings.
        """
        sim = euclidean(emb_1, emb_2)
        return sim
