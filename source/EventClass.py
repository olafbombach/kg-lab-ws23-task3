from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Union
import numpy as np

from source.Tokenizer import TokenSet, Tokenizer
from source.SearchEngine import SearchEngine
from source.Semantifier import Semantifier
from source.Encoder import Encoder

import polars as pl


@dataclass
class ProceedingsEvent:
    """
    The instance class of a Proceedings.com event.
    In this all information can be stored during one process run.
    """
    input_info: dict
    keywords: TokenSet = None

    full_title: str = None
    short_name: Optional[str] = None
    ordinal: Optional[str] = None
    part_of_series: Optional[str] = None
    country_name: Optional[str] = None
    country_short: Optional[str] = None
    city_name: Optional[str] = None
    year: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # after semantification
    configuration: Optional[Dict] = field(default_factory=dict)
    encode_map: Optional[Dict] = field(default_factory=dict)
    encodings: Optional[Dict] = field(default_factory=dict)

    def __repr__(self):
        attributes = asdict(self)
        attributes['input_info'] = 'Filled' if self.input_info != None else 'Unfilled'
        attributes['keywords'] = 'Filled' if self.keywords != None else 'Unfilled'
        attributes['configuration'] = 'Filled' if len(self.encode_map) > 0 else 'Unfilled'
        attributes['encodings'] = len(self.encodings) if len(self.encodings) > 0 else 'Unfilled'
        return f"ProceedingsEvent({attributes})"

    def __post_init__(self):
        tok = Tokenizer()
        self.keywords = tok.tokenizeProceedings(self.input_info)

    def apply_searchengine(self, se_instance: SearchEngine, max_search_hits: int = 5):
        """
        Applies the Searchengine to the ProceedingsEvent. Since the SearchEngine
        is initialized before you can take the instance and feed it as attribute here.
        Further you can specify the maximum number of hits that should be provided.
        If you want to include all search hits you can just set this number arbitrarily high.
        Caution: This will lead to a longer computation for the Semantifier!
        """
        search_hits = se_instance.search_set_of_tuples(self.keywords.tokens)
        if se_instance.get_dataset_name == "Wikidata":
            loe = ListOfEvents(source="Wikidata")
            for pos in range(search_hits.shape[0]):
                if pos < max_search_hits:
                    del_cols = ['conf_qid', 'country_qid', 'location_qid', 'score']
                    temp = search_hits.drop(del_cols).row(pos, named=True)
                    qid = search_hits.row(pos, named=True)['conf_qid']
                    wikievent = WikidataEvent(input_info=temp,
                                              qid=qid,
                                              keywords_score=search_hits.row(pos, named=True)['score'])
                    loe = loe + wikievent
                    del wikievent
                else:
                    break
        elif se_instance.get_dataset_name == "proceedings.com":
            loe = ListOfEvents(source="proceedings.com")
            for pos in range(search_hits.shape[0]):
                temp = search_hits.row(pos, named=True).pop('score')
                proceedingsevent = ProceedingsEvent(input_info=temp)
                loe = loe + proceedingsevent
                del proceedingsevent
        else:
            print("Something does not add up!")

        return loe

    def apply_semantifier(self, get_dict: bool = True):
        """
        Applies the Semantifier to the Proceedings Event.
        For this it takes the attribute input_info which is given from the data sources.
        """
        sf = Semantifier(dataset_name='proceedings.com')
        sf_output = sf.semantifier(self.input_info)

        self.full_title = str(sf_output.get('full_title')) if sf_output.get('full_title') != ("" or "None" or None) else None
        self.short_name = str(sf_output.get('short_name')) if sf_output.get('short_name') != ("" or "None" or None) else None
        self.ordinal = str(sf_output.get('ordinal')) if sf_output.get('ordinal') != ("" or "None" or None) else None
        self.part_of_series = str(sf_output.get('part_of_series')) if sf_output.get('part_of_series') != ("" or "None" or None) else None
        self.country_name = str(sf_output.get('country_name')) if sf_output.get('country_name') != ("" or "None" or None) else None
        self.country_short = str(sf_output.get('country_short')) if sf_output.get('country_short') != ("" or "None" or None) else None
        self.city_name = str(sf_output.get('city_name')) if sf_output.get('city_name') != ("" or "None" or None) else None
        self.year = str(sf_output.get('year')) if sf_output.get('year') != ("" or "None" or None) else None
        self.start_time = str(sf_output.get('start_time')) if sf_output.get('start_time') != ("" or "None" or None) else None
        self.end_time = str(sf_output.get('end_time')) if sf_output.get('end_time') != ("" or "None" or None) else None

        if get_dict:  # for encoding
            att_dict = asdict(self)
            att_dict.pop('input_info', None)
            att_dict.pop('keywords', None) 
            att_dict.pop('configuration', None)
            att_dict.pop('encode_map', None)
            att_dict.pop('encodings', None)         
        else:
            pass

        return att_dict
        

    def apply_encoder(self, dict_file):
        """
        At first creates an encoder map, which maps the QID of the Wikidata event
        to the corresponding proceedings event encoding.
        This is necessary when we want to create a good mutual comparison.
        Afterwards create the encodings for the unique configurations.
        These are then appended to the Attribute Encodings.
        """
        encodings = dict()
        enc = Encoder(dict_file=dict_file)  # initialize
        encoding_set = []  # create unique keys for the creation of encodings
        index = 0
        for item in self.configuration.keys():  # item is QID
            if self.configuration[item] not in encoding_set:
                encoding_set.append(self.configuration[item])
                self.encode_map[item] = "enc"+str(index)
                index += 1
            else:
                for prev_key, prev_val in self.configuration.items():
                    if prev_val == self.configuration[item]:
                        self.encode_map[item] = self.encode_map[prev_key]
                        break  # after first find
                    else:
                        pass
            
        for i, lst in enumerate(encoding_set):  # create encodings for unique key list
            bool_dict = dict()
            for ele in lst:
                bool_dict[ele] = True
            encoding = enc.get_bert_encoding(**bool_dict)  # dict unpacking
            encodings['enc'+str(i)] = encoding
        self.encodings = encodings

@dataclass
class WikidataEvent:
    """
    The instance class of a Wikidata event. 
    In this all information can be stored ruing one process run. 
    """
    input_info: dict
    qid: str
    keywords_score: float

    # after semantification
    full_title: str = None
    short_name: Optional[str] = None
    ordinal: Optional[str] = None
    part_of_series: Optional[str] = None
    country_name: Optional[str] = None
    country_short: Optional[str] = None
    city_name: Optional[str] = None
    year: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # after encoding
    encoding: Optional[np.array] = None
    similarity: Optional[float] = None

    def __repr__(self):
        attributes = asdict(self)
        attributes['input_info'] = 'Filled' if self.input_info != None else 'Unfilled'
        attributes['encoding'] = 'Filled' if isinstance(self.encoding, np.ndarray) else 'Unfilled'
        return f"WikidataEvent({attributes})"
    
    def apply_semantifier(self, get_dict: bool = True):
        """
        Applies the Semantifier to the Wikidata Event.
        For this it takes the attribute input_info which is given from the data sources.
        """
        sf = Semantifier(dataset_name='Wikidata')
        sf_output = sf.semantifier(self.input_info)
        
        self.full_title = str(sf_output.get('full_title')) if sf_output.get('full_title') != ("" or "None" or None) else None
        self.short_name = str(sf_output.get('short_name')) if sf_output.get('short_name') != ("" or "None" or None) else None
        self.ordinal = str(sf_output.get('ordinal')) if sf_output.get('ordinal') != ("" or "None" or None) else None
        self.part_of_series = str(sf_output.get('part_of_series')) if sf_output.get('part_of_series') != ("" or "None" or None) else None
        self.country_name = str(sf_output.get('country_name')) if sf_output.get('country_name') != ("" or "None" or None) else None
        self.country_short = str(sf_output.get('country_short')) if sf_output.get('country_short') != ("" or "None" or None) else None
        self.city_name = str(sf_output.get('city_name')) if sf_output.get('city_name') != ("" or "None" or None) else None
        self.year = str(sf_output.get('year')) if sf_output.get('year') != ("" or "None" or None) else None
        self.start_time = str(sf_output.get('start_time')) if sf_output.get('start_time') != ("" or "None" or None) else None
        self.end_time = str(sf_output.get('end_time')) if sf_output.get('end_time') != ("" or "None" or None) else None

        if get_dict:  # for encoding
            att_dict = asdict(self)
            att_dict.pop('input_info', None)
            att_dict.pop('keywords_score', None)
            att_dict.pop('encoding', None)         
            att_dict.pop('similarity', None)  
            
            return att_dict
        else:
            pass

    def apply_encoder(self, dict_file: dict, keyword_args: dict):       
        enc = Encoder(dict_file=dict_file)
        encoding = enc.get_bert_encoding(**keyword_args)
        self.encoding = encoding


@dataclass
class ListOfEvents:
    """
    The instance class of a list of events. 
    Either proceedings.com or Wikidata events are possible.
    We need this to save the information output of the SearchEngine.
    """
    source: str
    list_of_events: Optional[List[Union[ProceedingsEvent, WikidataEvent]]] = field(default_factory=list)
    list_of_dicts: Optional[List[dict]] = field(default_factory=list)
    configuration: Optional[Dict] = field(default_factory=dict)

    def __add__(self, other):
        """
        The method to add another event to the list.
        This method is necessary for the operations 
        that are carried out in dataclass methods.
        """
        if self.source == 'Wikidata':
            assert type(other) == WikidataEvent, "You can only add an instance of type WikidataEvent."
        elif self.source == 'proceedings.com':
            assert type(other) == ProceedingsEvent, "You can only add an instance of type Proceedings.com"
        self.list_of_events.append(other)
        return ListOfEvents(source=self.source, list_of_events=self.list_of_events)

    def __len__(self):
        """
        The method to evaluate the length of the List of events.
        """
        return len(self.list_of_events)

    def apply_semantifier(self, get_dict: bool = True):
        """
        Takes a list of events (LoE) and semantify them one by one.
        """
        list_of_dicts = []
        for entry in self.list_of_events:
            if type(entry) == WikidataEvent:
                dictionary = entry.apply_semantifier(get_dict=get_dict)
                list_of_dicts.append(dictionary)
        self.list_of_dicts = list_of_dicts

    def compute_configurations(self, pe: ProceedingsEvent) -> None:
        configuration = dict()
        # Proceedings keys
        available_data = asdict(pe)
        available_data.pop('input_info', None)
        available_data.pop('keywords', None)
        available_data.pop('configuration', None)
        available_data.pop('encodings', None)
        # Wikidata element keys
        for element in self.list_of_dicts:
            dict_of_entry = element  # copy
            qid = dict_of_entry.get('qid')
            # delete unneeded keys
            dict_of_entry.pop('qid', None)
            dict_of_entry.pop('keywords_score', None)
            for key in list(dict_of_entry):  # create copy with list
                if dict_of_entry[key] == None or available_data[key] == None:
                    dict_of_entry.pop(key, None)
                else:
                    pass

            configuration[qid] = list(dict_of_entry.keys())

        # set configuration to class attributes
        self.configuration = configuration
        pe.configuration = configuration
        
    def apply_encoder(self):
        """
        Applies the Encoder to the full List of Events.

        Please make sure that you previously created the configurations
        so that the encoding matches up with the ProceedingsEvent encoding.
        """
        for i, entry in enumerate(self.list_of_events):
            current_qid = entry.qid
            try:
                current_conf = self.configuration[current_qid]
            except:
                print("Something went wrong here")
                  # create encodings for unique key list
            bool_dict = dict()
            for ele in current_conf:
                bool_dict[ele] = True
            entry.apply_encoder(dict_file=self.list_of_dicts[i], keyword_args=bool_dict)         

@dataclass
class EventSeries:
    """
    Not sure yet, where we would have to use this.
    """
    collection: List[Union[ProceedingsEvent, WikidataEvent]]
