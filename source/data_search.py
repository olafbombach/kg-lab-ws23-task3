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
        self.flag_mask = None  # this is interesting since it can visualize how good the result of the SearchEngine is
        self.filtered_data = None  # this is the final outcome of the dataset search

    def _read_in_data(self) -> pd.DataFrame:
        """
            This method reads in data of the different sources and projects it as into pandas.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if self.dataset_name == 'Conference Corpus':
            path = "../datasets/.conferencecorpus/conf_corpus_data.csv"
            data = pd.read_csv(path, header=0, index_col=0)
        elif self.dataset_name == 'AIDA':
            # path = "../datasets/AIDA/Venues_Dataset202205/data/conferenceFolderStruct"
            pass
        elif self.dataset_name == 'proceedings.com':
            path = "../datasets/proceedings.com/all-nov-23.xlsx"
            data = pd.read_excel(path, engine='openpyxl')
        elif self.dataset_name == 'Wikidata':
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
            The number of hits (score) is then added to the filtered dataframe.
            It further sorts the dataframe according to the score
            (It is meant to be a private method since it is called in search_list originally.)
        """
        self.data = self.data.assign(score=np.sum(self.flag_mask, axis=1))
        #self.data.sort_values(by='score', ascending=False, inplace=True)
        return self.data

    def search_list(self, keywords: list) -> pd.DataFrame:
        """
            This method does the following:
            1.  Converts all dataframe columns to type string in order to better search for values
            2.  Searches for specific keywords in the specified dataframe using regex methods.
                If a match could be found, the position in the dataframe is marked (flag_mask with bool-values).
            3.  This is done for all strings of the keywords. The flag_mask is appended using logical_or.
            4.  After all keywords a score is computed using _mask_eval()
            5.  Filtering of all rows in which flag_mask is bigger than 0
            6.  Sorting of all rows based on score-value
        """

        for col in self.columns_sel:
            self.data[col] = self.data[col].astype(str)

        # this is a first easy approach.. we should include case distinction
        # where we stop the search after a given number of rows (e.g.)
        flag_mask = None
        for string in keywords:
            flag_mask = np.logical_or(flag_mask, np.column_stack([self.data[col].str.contains(string, na=False) for col in self.columns_sel]))
        self.flag_mask = flag_mask

        self.data = self._mask_eval()  # adds score as the last column
        self.filtered_data = self.data.loc[self.data['score'] > 0].copy()
        self.filtered_data.sort_values(by='score', ascending=False, inplace=True)  # sort according to score

        return self.filtered_data


se = SearchEngine(dataset_name='proceedings.com', fastsearch=True)
print(se.search_list(['QCMC', 'SIGIR']))
