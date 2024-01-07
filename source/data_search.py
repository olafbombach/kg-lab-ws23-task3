import re

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


class SearchEngine(object):
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

        self.dataset_name = dataset_name
        self.fastsearch = fastsearch
        self.data = self._read_in_data()
        self.columns_sel = self._get_columns_sel()
        self.hit_mask = None  # this is interesting since it can visualize how good the result of the SearchEngine is
        self.filtered_data = None  # this is the final outcome of the dataset search

    def _read_in_data(self) -> pd.DataFrame:
        """
            This method reads in data of the different sources and projects it as into pandas.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if self.dataset_name == 'Conference Corpus':
            try:
                path = "./datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pd.read_csv(path, header=0, index_col=0)
            except FileNotFoundError:
                path = "../datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pd.read_csv(path, header=0, index_col=0)
        elif self.dataset_name == 'AIDA':
            # csv or xsl not defined yet
            pass
        elif self.dataset_name == 'proceedings.com':
            try:
                path = "./datasets/proceedings.com/all-nov-23.xlsx"
                data = pd.read_excel(path, engine='openpyxl')
            except FileNotFoundError:
                path = "../datasets/proceedings.com/all-nov-23.xlsx"
                data = pd.read_excel(path, engine='openpyxl')
        elif self.dataset_name == 'Wikidata':
            try:
                path = './datasets/wikidata/wikidata_conf_data.csv'
                data = pd.read_csv(path, header=0, index_col=0)
            except FileNotFoundError:
                path = '../datasets/wikidata/wikidata_conf_data.csv'
                data = pd.read_csv(path, header=0, index_col=0)

        return data

    def _get_columns_sel(self) -> list:
        """
            This method determines the columns selection for the search.
            It is dependent on the attribute fastsearch since this determines which columns to include.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if not self.fastsearch:
            columns_sel = self.data.columns
        else:
            if self.dataset_name == 'Conference Corpus':
                columns_sel = ['name', 'acronym', 'title', 'sponsor']
            elif self.dataset_name == 'AIDA':
                columns_sel = self.data.columns  # not specified yet
            elif self.dataset_name == 'proceedings.com':
                columns_sel = ['Publisher', 'Conference Title', 'Series', 'Subject1']
            elif self.dataset_name == 'Wikidata':
                columns_sel = self.data.columns

        return columns_sel

    def _mask_eval(self) -> pd.DataFrame:
        """
            This method evaluates the quality of the found results with the SearchEngine.
            It returns the number of hits that a row had when using the list of keywords specified.
            The number of hits (score) is then added to the dataframe.
            (It is meant to be a private method since it is called in search_list originally.)
        """
        self.data = self.data.assign(score=np.sum(self.hit_mask, axis=1))
        return self.data

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

        for col in self.columns_sel:
            self.data[col] = self.data[col].astype(str)

        hit_mask = np.zeros(self.data.loc[:, self.columns_sel].shape)
        for string in keywords:
            hit_mask = hit_mask + np.column_stack([self.data[col].str.contains(string, flags=re.IGNORECASE, case=False, na=False, regex=True) for col in self.columns_sel])
        self.hit_mask = hit_mask.astype(dtype=int)

        self.data = self._mask_eval()  # adds score as the last column
        self.filtered_data = self.data.loc[self.data['score'] >= self.data['score'].max()/2].copy()  # only show rows that have at least half of the maximum score value
        self.filtered_data.sort_values(by='score', ascending=False, inplace=True)  # sort according to score

        return self.filtered_data


se = SearchEngine(dataset_name='Wikidata', fastsearch=False)
print(se.search_list(['25th', 'twentyfifth', '2017', 'Euromicro International Conference on Parallel, Distributed and Network-based Processing', 'PDP', '6. March', '8. March', '06.03.', '08.03', 'St. Petersburg', 'Russia', 'Euromicro', 'Parallel, Distributed and Network-based Processing']))
