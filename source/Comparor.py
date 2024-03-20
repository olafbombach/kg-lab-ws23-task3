from source.EventClass import ProceedingsEvent, ListOfEvents, WikidataEvent

from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import numpy as np

class Comparor:

    def __init__(self, pe: ProceedingsEvent, loe: ListOfEvents):
        self.pe = pe
        self.loe = loe
        self.optimal_val = None

    def add_measure_as_attribute(self, metric: str) -> None:
        """
        Get the optimal similarity for the List of Events 
        regarding the ProceedingsEvents. Possible values for metric are 
        \"euc\" and \"cos\".
        """
        assert metric in {"cos", "euc"}, "Your method is not supported."
        
        if metric == "cos":
            for entry in self.loe.list_of_events:
                qid = entry.qid
                enc_number = self.pe.encode_map.get(qid)
                pe_encoding = self.pe.encodings.get(enc_number)
                sim = Comparor.cos_similarity(pe_encoding, entry.encoding)
                entry.similarity = sim
        elif metric == "euc":
            for entry in self.loe.list_of_events:
                qid = entry.qid
                enc_number = self.pe.encode_map.get(qid)
                pe_encoding = self.pe.encodings.get(enc_number)
                sim = Comparor.euclidean_similarity(pe_encoding, entry.encoding)
                entry.similarity = sim
        else:
            pass

    def get_optimal_similarity(self, metric: str) -> WikidataEvent:
        """
        Returns the optimal fit for the given ProceedingsEvent. 
        This method will give the optimal WikidataEvent and its attributes.
        """
        assert metric in {"cos", "euc"}, "Your method is not supported."
        
        current_optimal = self.loe.list_of_events[0]  # initialization
        optimal_val = self.loe.list_of_events[0].similarity
        
        if metric == "cos":   
            for entry in self.loe.list_of_events:
                if current_optimal.similarity < entry.similarity:
                    optimal_val = entry.similarity
                    current_optimal = entry
        elif metric == "euc":
            for entry in self.loe.list_of_events:
                if current_optimal.similarity > entry.similarity:
                    optimal_val = entry.similarity
                    current_optimal = entry
        else:
            pass
        self.optimal_val = optimal_val
        return current_optimal   
    
    def case_decision(self, metric: str) -> str:
        """
        This method determines whether this ProceedingsEvent could be found in
        the Wikidata Database. 
        Keep in mind, that this function highly depends on hyperparameters.
        """
        assert metric in {"cos", "euc"}, "Your method is not supported."

        if metric == "cos":
            if self.optimal_val < 0.92:
                return "Unfound"
            elif 0.92 <= self.optimal_val < 0.98:
                return "Unclear"
            elif self.optimal_val >= 0.98:
                return "Found"
            else:
                "This should not show up.."
        elif metric == "euc":
            if self.optimal_val > 3.5:
                return "Unfound"
            elif 3.5 >= self.optimal_val > 1.8:
                return "Unclear"
            elif self.optimal_val <= 1.8:
                return "Found"
            else:
                "This should not show up.."
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
    
    @property
    def get_optimal_val(self):
        return self.optimal_val
