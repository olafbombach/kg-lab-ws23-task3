import polars as pl


class Preprocessor:
    def __init__(self, dataset_name: str) -> None:
        assert dataset_name in ['Conference Corpus', 'proceedings.com', 'Wikidata'],\
            "Please specify a dataset which is part of " \
            "[\'Conference Corpus\', \'proceedings.com\', \'Wikidata\']"

        self._dataset_name = dataset_name
        self._data = self._read_in_data()
        self._preproc_data = None

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

    def apply_pipeline(self) -> None:
        Preprocessor.delete_columns(self)

    def delete_columns(self) -> None:
        self._preproc_data = self._data.drop("")

    def get_dataframe(self, preproc: bool = True) -> pl.DataFrame:
        if not preproc:
            return print(self._data)
        return print(self._preproc_data)


pp = Preprocessor("Wikidata")
pp.apply_pipeline()
pp.get_dataframe()
