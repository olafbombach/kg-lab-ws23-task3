import re
import polars as pl
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
        assert dataset_name in ['Conference Corpus', 'proceedings.com', 'Wikidata'],\
            "Please specify a dataset which is part of " \
            "[\'Conference Corpus\', \'proceedings.com\', \'Wikidata\']"

        self._dataset_name = dataset_name
        self._fastsearch = fastsearch
        self._data = self._read_in_data()
        self._columns_sel = self._get_columns_sel()
        self._hit_mask = None
        self._filtered_data = None

    def _read_in_data(self) -> pl.DataFrame:
        """
            This method reads in data of the different sources and projects it in polars.
            (It is meant to be a private method since it is called in the __init__ method.)
        """
        if self._dataset_name == 'Conference Corpus':
            try:
                path = "./datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pl.read_csv(path, has_header=True)
            except FileNotFoundError:
                path = "../datasets/.conferencecorpus/conf_corpus_data.csv"
                data = pl.read_csv(path, has_header=True)
        elif self._dataset_name == 'proceedings.com':
            try:
                path = "./datasets/proceedings.com/all-nov-23.xlsx"
                data = pl.read_excel(path, engine='openpyxl')
            except FileNotFoundError:
                path = "../datasets/proceedings.com/all-nov-23.xlsx"
                data = pl.read_excel(path, engine='openpyxl')
        elif self._dataset_name == 'Wikidata':
            try:
                path = './datasets/wikidata/wikidata_conf_data.csv'
                data = pl.read_csv(path, has_header=True)
            except FileNotFoundError:
                path = '../datasets/wikidata/wikidata_conf_data.csv'
                data = pl.read_csv(path, has_header=True)
        return data

    def _get_columns_sel(self) -> list[str]:
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
            elif self._dataset_name == 'proceedings.com':
                columns_sel = ['Publisher', 'Conference Title', 'Book Title', 'Series', 'Mtg Year', 'Publ Year', 'Subject1']
            elif self._dataset_name == 'Wikidata':
                dont_include = {"WikiCFP_identifier", "DBLP_identifier"}
                columns_sel = [col for col in self._data.columns if col not in dont_include]
        return columns_sel

    def _mask_eval(self) -> pl.DataFrame:
        """
            This method evaluates the quality of the found results with the SearchEngine.
            It returns the number of hits that a row had when using the keywords specified in the search method.
            The number of hits (score) is then added to the polars dataframe.
            (It is meant to be a private method since it is called in search_dict originally.)
        """
        self._data = self._data.with_columns(pl.Series(name="score",
                                                       values=np.sum(self._hit_mask, axis=1),
                                                       dtype=pl.Float64))
        return self._data

    @get_timer
    def search_dict(self, keywords_dict: dict[str, float], threshold_method: str = "three quarter") -> pl.DataFrame:
        """
            The method does the following:
            1.  Converts all selected dataframe columns to type string in order to better search for values.
            2.  Searches for specific keywords in the specified dataframe using regex methods.
                If a match could be found, the position in the dataframe is marked (hit_mask with bool-values).
            3.  This is done for all strings of the keywords and multiplied according to its weight.
                The hit_mask is appended using normal sum.
            4.  After all keywords a score is computed using _mask_eval().
            5.  Filtering of all rows in which hit_mask for one column has at least half of the maximum score.
            6.  Sorting of all rows based on score-value (descending).
        """
        assert threshold_method in ["three quarter", "half", "top 5"], \
            "This threshold method, does not exist. Please select one of the following: " \
            "[\"three quarter\", \"half\", \"top 5\"]."

        self._hit_mask = None  # reset self._hit_mask
        self._filtered_data = None  # reset self._filtered_data

        if set(self._data[self._columns_sel].dtypes) != {pl.String}:
            mapper_for_cols = {key: pl.String for key in self._columns_sel}
            self._data = self._data.cast(mapper_for_cols, strict=True)

        hit_mask = np.zeros((self._data.shape[0], len(self._columns_sel)))
        for string in keywords_dict.keys():
            addition = np.column_stack([self._data[column].str.contains(r"(?i)"+string, strict=True)
                                       .replace({None: False}) for column in self._columns_sel])
            hit_mask = hit_mask + addition * keywords_dict[string]

        self._hit_mask = hit_mask.astype(dtype=int)

        self._data = self._mask_eval()  # adds score as the last column

        # carries out the filtering based on determined method
        if threshold_method == "half":
            threshold = self._data.select(pl.max("score")) * 1/2
            self._filtered_data = self._data.filter(pl.col('score') >= threshold)
            self._filtered_data = self._filtered_data.sort('score', descending=True)
        elif threshold_method == "three quarter":
            threshold = self._data.select(pl.max("score")) * 3/4
            self._filtered_data = self._data.filter(pl.col('score') >= threshold)
            self._filtered_data = self._filtered_data.sort('score', descending=True)
        elif threshold_method == "top 5":
            self._filtered_data = self._data.sort('score', descending=True)
            self._filtered_data = self._filtered_data.head(5)

        return self._filtered_data

'''
input_query = {'25th': 40, 'twentyfifth': 40, '2017': 70,
               'Euromicro International Conference on Parallel, Distributed and Network-based Processing': 100,
               'PDP': 70, '6. March': 75, '8. March': 75, '06.03.': 75, '08.03': 75, 'St. Petersburg': 60, 'Russia': 60,
               'Euromicro': 50, 'Parallel, Distributed and Network-based Processing': 60}

se = SearchEngine("Wikidata", fastsearch=True)
print(se.search_dict(input_query, threshold_method="three quarter"))
print(se.search_dict(input_query, threshold_method="three quarter"))
'''
