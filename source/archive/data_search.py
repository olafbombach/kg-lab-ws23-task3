import re
import json
import pandas as pd
import numpy as np
from timeit import default_timer as timer


# create wrapper to visualize elapsed time
def get_timer(func):
    def wrapper(*args, **kwargs):
        t1 = timer()
        result = func(*args, **kwargs)
        t2 = timer()
        print(f'Search executed in {(t2-t1):.4f}s.')
        return result

    return wrapper


class SearchEngine:
    """
        An operator that takes a list as a search filter and then searches for these keywords in a specified dataset.
        So for you can only specify the datasets Wikidata, Conference Corpus and proceedings.com
    """

    def __init__(self, dataset_name: str, fastsearch: bool = False):
        """
        Initialize the SearchEngine.
        It takes the dataset_name and a boolean value that determines if we should use fastsearch.
        Caution: fastsearch=True restricts the columns and thus could lead to false results.
        """
        assert dataset_name in ['Conference Corpus', 'AIDA', 'proceedings.com', 'Wikidata'], \
            "Please specify a dataset which is part of " \
            "[\'Conference Corpus\', \'AIDA\', \'proceedings.com\', \'Wikidata\']"

        self._dataset_name = dataset_name
        self._fastsearch = fastsearch
        self._data = self._read_in_data()
        self._columns_sel = self._get_columns_sel()
        self._hit_mask = None  # this is interesting since it can visualize how good the result of the SearchEngine is
        self._filtered_data = None  # this is the final outcome of the dataset search

    def _read_in_data(self) -> pd.DataFrame:
        """
            This method reads in data of the different sources and projects it as into pandas.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if self._dataset_name == 'Conference Corpus':
            try:
                path = "./datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pd.read_csv(path, header=0, index_col=0)
            except FileNotFoundError:
                path = "../../datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pd.read_csv(path, header=0, index_col=0)
        elif self._dataset_name == 'AIDA':
            # csv or xsl not defined yet
            pass
        elif self._dataset_name == 'proceedings.com':
            try:
                path = "./datasets/proceedings.com/all-nov-23.xlsx"
                data = pd.read_excel(path, engine='openpyxl')
            except FileNotFoundError:
                path = "../../datasets/proceedings.com/all-nov-23.xlsx"
                data = pd.read_excel(path, engine='openpyxl')
        elif self._dataset_name == 'Wikidata':
            try:
                path = './datasets/wikidata/wikidata_conf_data.csv'
                data = pd.read_csv(path, header=0, index_col=0)
            except FileNotFoundError:
                path = '../../datasets/wikidata/wikidata_conf_data.csv'
                data = pd.read_csv(path, header=0, index_col=0)

        return data

    def _get_columns_sel(self) -> list:
        """
            This method determines the columns selection for the search.
            It is dependent on the attribute fastsearch since this determines which columns to include.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if not self._fastsearch:
            columns_sel = self._data.columns
        else:
            if self._dataset_name == 'Conference Corpus':
                columns_sel = ['name', 'acronym', 'title', 'sponsor']
            elif self._dataset_name == 'AIDA':
                columns_sel = self._data.columns  # not specified yet
            elif self._dataset_name == 'proceedings.com':
                columns_sel = ['Publisher', 'Conference Title', 'Series', 'Subject1']
            elif self._dataset_name == 'Wikidata':
                columns_sel = self._data.columns

        return columns_sel

    def _mask_eval(self) -> pd.DataFrame:
        """
            This method evaluates the quality of the found results with the SearchEngine.
            It returns the number of hits that a row had when using the keywords specified in the search method.
            The number of hits (score) is then added to the dataframe.
            (It is meant to be a private method since it is called in search_list and search_dict originally.)
        """
        self._data = self._data.assign(score=np.sum(self._hit_mask, axis=1))
        return self._data

    @get_timer
    def search_list(self, keywords: list) -> pd.DataFrame:
        """
            This method does the following:
            1.  Converts all selected dataframe columns to type string in order to better search for values.
            2.  Searches for specific keywords in the specified dataframe using regex methods.
                If a match could be found, the position in the dataframe is marked (hit_mask with bool-values).
            3.  This is done for all strings of the keywords. The hit_mask is appended using normal sum.
            4.  After all keywords a score is computed using _mask_eval().
            5.  Filtering of all rows in which hit_mask for one column has at least half of the maximum score.
            6.  Sorting of all rows based on score-value (descending).
        """

        self._hit_mask = None  # reset _hit_mask

        for col in self._columns_sel:
            self._data[col] = self._data[col].astype(str)

        hit_mask = np.zeros(self._data.loc[:, self._columns_sel].shape)
        for string in keywords:
            hit_mask = hit_mask + np.column_stack([self._data[col].str.contains(string, flags=re.IGNORECASE, case=False, na=False, regex=True) for col in self._columns_sel])
        self._hit_mask = hit_mask.astype(dtype=int)

        self._data = self._mask_eval()  # adds score as the last column
        self._filtered_data = self._data.loc[self._data['score'] >= self._data['score'].max()/2].copy()  # only show rows that have at least half of the maximum score value
        self._filtered_data.sort_values(by='score', ascending=False, inplace=True)  # sort according to score

        return self._filtered_data

    @get_timer
    def search_dict(self, keywords_dict: dict) -> pd.DataFrame:
        """
            This method is the pendant to search_list(). The dictionary only enables to use weights for keywords,
            which optimizes the search. The method does the following:
            1.  Converts all selected dataframe columns to type string in order to better search for values.
            2.  Searches for specific keywords in the specified dataframe using regex methods.
                If a match could be found, the position in the dataframe is marked (hit_mask with bool-values).
            3.  This is done for all strings of the keywords and multiplied according to its weight.
                The hit_mask is appended using normal sum.
            4.  After all keywords a score is computed using _mask_eval().
            5.  Filtering of all rows in which hit_mask for one column has at least half of the maximum score.
            6.  Sorting of all rows based on score-value (descending).

            :params: keywords_dict should have keywords as keys and weights as values.
        """
        self._hit_mask = None  # reset _hit_mask

        for col in self._columns_sel:
            self._data[col] = self._data[col].astype(str)

        hit_mask = np.zeros(self._data.loc[:, self._columns_sel].shape)
        for string in keywords_dict.keys():
            hit_mask = hit_mask + np.column_stack([self._data[col].str.contains(string, flags=re.IGNORECASE, case=False, na=False, regex=True) for col in self._columns_sel]) * keywords_dict[string]
        self._hit_mask = hit_mask.astype(dtype=int)

        self._data = self._mask_eval()  # adds score as the last column
        self._filtered_data = self._data.loc[self._data['score'] >= self._data[
            'score'].max() / 2].copy()  # only show rows that have at least half of the maximum score value
        self._filtered_data.sort_values(by='score', ascending=False, inplace=True)  # sort according to score

        return self._filtered_data


'''
input_query = {'25th': 40, 'twentyfifth': 40, '2017': 70,
               'Euromicro International Conference on Parallel, Distributed and Network-based Processing': 100,
               'PDP': 70, '6. March': 75, '8. March': 75, '06.03.': 75, '08.03': 75, 'St. Petersburg': 60, 'Russia': 60,
               'Euromicro': 50, 'Parallel, Distributed and Network-based Processing': 60}

se = SearchEngine(dataset_name='proceedings.com', fastsearch=False)
result = se.search_dict(input_query)
print(result)
'''
