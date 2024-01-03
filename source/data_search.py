import pandas as pd
import numpy as np


class Synonymator:
    """
        An operator that takes a string as an input and generates synonyms that can be used for better search results.
        Since there might be differences between synonyms for series or conferences it is better to create two functions here.
    """

    def series_synonyms(self, text : str) -> list:
        pass


    def conf_synonyms(self, text : str) -> list:
        pass


class SearchEngine:
    """
        An operator that takes the previously created list as a search filter and then searches for these keywords in the specified dataset.
        This might include a __init__ function where we declare which datasets is tackled...
    """
    def __init__(self, dataset : str):
        """
            initialize the SearchEngine. It takes the name of the dataset as an argument
        """
        self.dataset = dataset
        assert self.dataset in ['Conference Corpus', 'AIDA', 'proceedings.com', 'Wikidata'], "Please specify a dataset which is part of [\'Conference Corpus\', \'AIDA\', \'proceedings.com\', \'Wikidata\']"


    def read_in_data(self) -> pd.DataFrame:
        """
            reads in data of the different sources and projects it as a dataframe
        """
        if self.dataset == 'Conference Corpus':
            path = '..\\datasets\\.conferencecorpus\\conf_corpus_data.csv'
            data = pd.read_csv(path, header=0, index_col=0)
            return data

        elif self.dataset == 'AIDA':
            path = '..\\datasets\\AIDA\\Venues_Dataset202205\\data\\conferenceFolderStruct'
            pass

        elif self.dataset == 'proceedings.com':
            path = '..\\datasets\\proceedings.com\\all-nov-23.xlsx'
            data = pd.read_excel(path, engine='openpyxl')
            return data

        elif self.dataset == 'Wikidata':
            path = '..\\datasets\\wikidata\\wikidata_conf_data.csv'
            data = pd.read_csv(path, header=0, index_col=0)
            return data


    def search_list(self, data : pd.DataFrame, keywords : list) -> pd.DataFrame:
        """
            1. converts all dataframe columns to type string in order to better search
            2. searches for specific keywords in the specified dataframe using regex methods
        """
        for col in data.columns:
            data[col] = data[col].astype(str)

        # this is a first easy approach.. we should include case distinction where we stop the search after a given number of rows (e.g.)
        for string in keywords:
            mask = np.column_stack([data[col].str.contains(string, na=False) for col in data.columns])

        filtered_data = data.loc[mask.any(axis=1)]

        return filtered_data