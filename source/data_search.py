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