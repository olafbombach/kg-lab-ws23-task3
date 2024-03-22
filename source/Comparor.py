from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import numpy as np
import orjson

from source.HelperFunctions import find_root_directory
from source.EventClass import ProceedingsEvent, ListOfEvents, WikidataEvent

class Comparor:
    """
    The class to compare the Proceedings.com event with the found Wikidata events
    of the ListOfEvents.
    """
    def __init__(self, pe: ProceedingsEvent, loe: ListOfEvents):
        """
        Initialize by feeding in the Proceedings.com event and the ListOfEvents instances.
        """
        self.pe = pe
        self.loe = loe
        self.optimal_val = None
        self.current_optimal = None
        self.decision = None
        self.current_dict = dict()

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
        self.current_optimal = current_optimal
        return current_optimal   
    
    def case_decision(self, metric: str):
        """
        This method determines whether this ProceedingsEvent could be found in
        the Wikidata Database. 
        It further creates the dictionary that will get uploaded to the
        corresponding json-file.
        Keep in mind, that this function highly depends on hyperparameters.
        """
        assert metric in {"cos", "euc"}, "Your method is not supported."

        if metric == "cos":
            if self.optimal_val < 0.92:
                self.decision = "Unfound"
            elif 0.92 <= self.optimal_val < 0.98:
                self.decision = "Unclear"
            elif self.optimal_val >= 0.98:
                self.decision = "Found"
            else:
                print("This should not show up...")
        elif metric == "euc":
            if self.optimal_val > 3.5:
                self.decision = "Unfound"
            elif 3.5 >= self.optimal_val > 1.8:
                self.decision = "Unclear"
            elif self.optimal_val <= 1.8:
                self.decision = "Found"
            else:
                print("This should not show up...")
        else:
            pass
        
        # prepare the current_dictionary for the json-upload
        if self.decision == "Unfound":
            self.current_dict = self.pe.get_signatures
        elif self.decision == "Unclear":
            interim_dict = dict()
            # here we create a dict of dicts, since we have multiple Wikidata entries to look at
            interim_dict['proc_event'] = self.pe.get_signatures
            interim_dict['loe'] = self.loe.get_dict_of_signatures
            self.current_dict = interim_dict
            pass
        elif self.decision == "Found":
            interim_dict = self.pe.get_signatures
            interim_dict['wd_qid'] = self.current_optimal.qid
            self.current_dict = interim_dict
        else:
            print("This should not happen...")

        return self.decision

    def result_to_json(self):
        """
        Writes the result to the corresponding directory in results/.
        Further distinguishes between the cases.
        """
        general_path = find_root_directory() / "results"

        if self.decision == "Unfound":
            file_path = general_path / "unfound_entries" / "upload.json"
        elif self.decision == "Unclear":
            file_path = general_path / "unclear_entries" / "manual.json"
        elif self.decision == "Found":
            file_path = general_path / "found_entries" / "upload.json"
        else:
            print("This should not happen...")
        
        # first read in current json-file to get cumulated_dict
        try:
            with open(file_path, encoding="utf-8") as f:
                json_str = f.read()
                if not json_str:
                    # If the file is empty, set cumulated_dict to an empty dictionary
                    cumulated_dict = dict()
                else:
                    # Load the cache from the existing file
                    cumulated_dict = orjson.loads(json_str)
        except FileNotFoundError:
            # Handle case where file does not exist -> will be created later
            cumulated_dict = dict()
        except Exception as e:
            # Handle other exceptions (e.g., invalid JSON data)
            print(f"Error loading json-file due to {e}")

        cumulated_dict[self.pe.isbn] = self.current_dict

        try:
            with open(file_path, 'wb') as f:
                json_str = orjson.dumps(cumulated_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
                f.write(json_str)
        except Exception as e:
            raise Exception(f"Error updating json-file due to {e}")

        

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
