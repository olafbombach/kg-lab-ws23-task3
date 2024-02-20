from dataclasses import dataclass, field, asdict
from typing import Optional, List, Union
import json
import numpy as np

from source.Tokenizer import TokenSet, Tokenizer
from source.SearchEngine import SearchEngine
from source.Semantifier import Semantifier
from source.Encoder import Encoder

from datasets.api_secrets import API_KEY
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
    country_identifier: Optional[str] = None
    city_name: Optional[str] = None
    year: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # after encoding
    encoding: Optional[np.array] = None

    def __repr__(self):
        attributes = asdict(self)
        #attributes['input_info'] = 'Filled' if self.input_info != None else 'Unfilled'
        #attributes['keywords'] = 'Filled' if self.keywords != None else 'Unfilled'
        attributes['encoding'] = 'Filled' if isinstance(self.encoding, np.ndarray) else 'Unfilled'
        return f"ProceedingsEvent({attributes})"

    def __post_init__(self):
        self.keywords = Tokenizer.tokenizeProceedings(self.input_info)

    def apply_searchengine(self, se_instance: SearchEngine, max_search_hits: int = 5):
        search_hits = se_instance.search_set_of_tuples(self.keywords.tokens)
        if se_instance.get_dataset_name == "Wikidata":
            loe = ListOfEvents(source="Wikidata")
            for pos in range(search_hits.shape[0]):
                if pos < max_search_hits:
                    temp = search_hits.drop('score').row(pos, named=True)
                    wikievent = WikidataEvent(input_info=temp,
                                              keywords_score=search_hits.row(pos, named=True)['score'])
                    loe = loe + wikievent
                    del wikievent
        elif se_instance.get_dataset_name == "proceedings.com":
            loe = ListOfEvents(source="proceedings.com")
            for pos in range(search_hits.shape[0]):
                temp = search_hits.row(pos, named=True).pop('score')
                proceedingsevent = ProceedingsEvent(input_info=temp)
                loe = loe + proceedingsevent
                del proceedingsevent
        return loe

    def apply_semantifier(self, get_dict: bool = True):
        sf = Semantifier(dataset_name='proceedings.com')
        sf_output = sf.semantifier(self.input_info,
                                            API_KEY)
        self.full_title = sf_output['full_title']
        self.short_name = sf_output['short_name']
        self.ordinal = sf_output['ordinal']
        self.part_of_series = sf_output['part_of_series']
        self.country_name = sf_output['country_name']
        self.country_identifier = sf_output['country_identifier']
        self.city_name = sf_output['city_name']
        self.year = sf_output['year']
        self.start_time = sf_output['start_time']
        self.end_time = sf_output['end_time']

        if get_dict:
            # I maybe have to enhance this with other keys
            att_dict = asdict(self)
            att_dict.pop('input_info', None)
            att_dict.pop('keywords', None) 
            att_dict.pop('encoding', None)           
            return att_dict
        

    def apply_encoder(self, dict_file: dict):
        enc = Encoder(dict_file=dict_file)
        encoding = enc.get_bert_encoding(city_name=True, year=True, full_title=True)
        self.encoding = encoding



@dataclass
class WikidataEvent:
    """
    The instance class of a Wikidata event. 
    In this all information can be stored ruing one process run. 
    """
    input_info: dict
    keywords_score: Optional[float] = None
    keywords : Optional[TokenSet] = None

    # after semantification
    full_title: str = None
    short_name: Optional[str] = None
    ordinal: Optional[str] = None
    part_of_series: Optional[str] = None
    country_name: Optional[str] = None
    country_identifier: Optional[str] = None
    city_name: Optional[str] = None
    year: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # after encoding
    encoding: Optional[np.array] = None

    def __repr__(self):
        attributes = asdict(self)
        #attributes['input_info'] = 'Filled' if self.input_info != None else 'Unfilled'
        #attributes['keywords'] = 'Filled' if self.keywords != None else 'Unfilled'
        attributes['encoding'] = 'Filled' if isinstance(self.encoding, np.ndarray) else 'Unfilled'
        return f"WikidataEvent({attributes})"
        

    # actually this should not be in post_init since we initialize this often
    '''
    def __post_init__(self):
        current_string = ""
        for i, info in enumerate(self.input_info.values()):
            if i > 0:
                current_string = current_string + info + ", "
        current_string = current_string.replace(", , , , ,", ",")
        current_string = current_string.replace(", , , ,", ",")
        current_string = current_string.replace(", , ,", ",")
        current_string = current_string.replace(", ,", ",")
        if current_string.endswith(", "):
            current_string = current_string.rstrip(", ")
        
        tokenset = Tokenizer.synonymes(current_string)
        self.keywords = tokenset
    '''

    def apply_searchengine(self, se_instance: SearchEngine, max_search_hits: int = 5):
        search_hits = se_instance.search_set_of_tuples(self.keywords.tokens)
        if se_instance.get_dataset_name == "Wikidata":
            loe = ListOfEvents(source="Wikidata")
            for pos in range(search_hits.shape[0]):
                if pos < max_search_hits:
                    temp = search_hits.row(pos, named=True).pop('score')
                    wikievent = WikidataEvent(input_info=temp,
                                              keywords_score=search_hits.row(pos, named=True)['score'])
                    loe = loe + wikievent
                    del wikievent
        elif se_instance.get_dataset_name == "proceedings.com":
            loe = ListOfEvents(source="proceedings.com")
            for pos in range(search_hits.shape[0]):
                temp = search_hits.row(pos, named=True).pop('score')
                proceedingsevent = ProceedingsEvent(input_info=temp)
                loe = loe + proceedingsevent
                del proceedingsevent
        return loe
    
    def apply_semantifier(self, get_dict: bool = True):
        sf = Semantifier(dataset_name='Wikidata')
        sf_output = sf.semantifier(self.input_info,
                       API_KEY)
        
        self.full_title = sf_output['full_title']
        self.short_name = sf_output['short_name']
        self.ordinal = sf_output['ordinal']
        self.part_of_series = sf_output['part_of_series']
        self.country_name = sf_output['country_name']
        self.country_identifier = sf_output['country_identifier']
        self.city_name = sf_output['city_name']
        self.year = sf_output['year']
        self.start_time = sf_output['start_time']
        self.end_time = sf_output['end_time']

        if get_dict:
            # I maybe have to enhance this with other keys
            att_dict = asdict(self)
            att_dict.pop('input_info', None)
            att_dict.pop('keywords', None) 
            att_dict.pop('encoding', None)           
            return att_dict


    def apply_encoder(self, dict_file: dict):       
        enc = Encoder(dict_file=dict_file)
        encoding = enc.get_bert_encoding(city_name=True, year=True, full_title=True)
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

    def apply_semantifier(self, get_list: bool = True):
        """
        Takes a list of events (LoE) and semantify them one by one.
        
        Next idea: first changing them to a dataframe and
        then semantifying them all together.
        """
        list_of_dicts = []
        for entry in self.list_of_events:
            if type(entry) == WikidataEvent:
                dictionary = entry.apply_semantifier(get_dict=get_list)
                list_of_dicts.append(dictionary)
        self.list_of_dicts = list_of_dicts
        """list_of_input_info = []
        for entry in self.list_of_events:
            list_of_input_info.append(entry.input_info)
        df = pl.from_dicts(list_of_input_info)
        print(df.shape)
        sf_output = Semantifier.semantifier(df, 
                                            user_key=API_KEY, 
                                            dataset_name=self.source)
        print((sf_output['conferences']))
        for entry in sf_output['conferences']:"""

    def apply_encoder(self):
        for i, entry in enumerate(self.list_of_events):
            entry.apply_encoder(dict_file=self.list_of_dicts[i])
            

@dataclass
class EventSeries:
    """
    Not sure yet, where we would have to use this.
    """
    collection: List[Union[ProceedingsEvent, WikidataEvent]]
