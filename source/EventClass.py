from dataclasses import dataclass, field
from typing import Optional, List, Union

from source.Tokenizer import TokenSet, Tokenizer
from source.SearchEngine import SearchEngine
import polars as pl


@dataclass
class ProceedingsEvent:
    """
    The instance class of a Proceedings.com event.
    In this all information can be stored during one process run.
    """
    input_info: dict
    #keywords: TokenSet = None

    full_title: str = None
    short_name: Optional[str] = None
    ordinal: Optional[int] = None
    part_of_series: Optional[str] = None
    country_name: Optional[str] = None
    country_identifier: Optional[str] = None
    city_name: Optional[str] = None
    main_object: Optional[str] = None
    year: Optional[int] = None
    start_time = None
    end_time = None

    def __post_init__(self):
        #self.keywords = Tokenizer.synonymes(str(self.input_info.values()))
        pass

    def apply_searchengine(self, se_instance: SearchEngine):
        search_hits = se_instance.search_set_of_tuples(self.keywords.tokens)
        if se_instance.get_dataset_name == "Wikidata":
            loe = ListOfEvents(source="Wikidata")
            for pos in range(search_hits.shape[0]):
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

    def apply_semantifier(self):
        pass

    def apply_encoder(self):
        pass

    '''
    def apply_semantifier(self):
        se = NLP()
        output = se.semantify(self.input_info)
        self.full_title = output['full_title']

        self.full_title: str = None
        self.short_name: Optional[str] = None
        ordinal: Optional[int] = None
        part_of_series: Optional[str] = None
        country_name: Optional[str] = None
        city_name: Optional[str] = None
        main_object: Optional[str] = None
        year: Optional[int] = None
        start_time = None
        end_time = None

    def apply_encoder(self):
    '''


@dataclass
class WikidataEvent:
    """
    The instance class of a Wikidata event. 
    In this all information can be stored ruing one process run. 
    """
    input_info: dict
    keywords_score: Optional[float] = None

    # after semantification
    full_title: str = None
    short_name: Optional[str] = None
    ordinal: Optional[int] = None
    part_of_series: Optional[str] = None
    country_name: Optional[str] = None
    city_name: Optional[str] = None
    main_object: Optional[str] = None
    year: Optional[int] = None
    start_time = None
    end_time = None

    def apply_searchengine(self, se_instance):
        pass


@dataclass
class ListOfEvents:
    """
    The instance class of a list of events. 
    Either proceedings.com or Wikidata events are possible.
    We need this to save the information output of the SearchEngine.
    """
    source: str
    list_of_events: Optional[List[Union[ProceedingsEvent, WikidataEvent]]] = field(default_factory=list)

    def __add__(self, other):
        """
        The method to add another event to the list.
        This method is necessary for the operations 
        that are carried out in dataclass methods.
        """
        if self.source is 'Wikidata':
            assert type(other) is WikidataEvent, "You can only add an instance of type WikidataEvent."
        elif self.source is 'proceedings.com':
            assert type(other) == ProceedingsEvent, "You can only add an instance of type Proceedings.com"
        self.list_of_events.append(other)
        return ListOfEvents(source=self.source, list_of_events=self.list_of_events)

    def __len__(self):
        """
        The method to evaluate the length of the List of events.
        """
        return len(self.list_of_events)

    def apply_semantifier(self):
        """
        Takes a list of events and semantify them.
        """
        pass


@dataclass
class EventSeries:
    """
    Not sure yet, where we would have to use this.
    """
    collection: List[Union[ProceedingsEvent, WikidataEvent]]


def main():
    se = SearchEngine('Wikidata')
    print(se.get_dataset_name)



if __name__ == "__main__":
    main()
