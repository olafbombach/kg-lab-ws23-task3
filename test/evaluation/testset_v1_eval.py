from source.synonymes import Synonymes
from source.data_search_opt import SearchEngine, get_timer
from source.Evaluator import Evaluator
import polars as pl
import numpy as np


@get_timer
def evaluate_testset_v1(testset_file: str = r"../datasets/wikidata/testset_v1_opt.csv"):
    # se_pro = SearchEngine('proceedings.com')
    se_wiki = SearchEngine('Wikidata', fastsearch=True)

    testset = pl.read_csv(testset_file, has_header=True, separator=';')
    testset = testset.drop("", "WikiCFP_identifier", "DBLP_identifier", "title")  # no index needed
    testset = testset.with_columns(pl.col('beginnings').cast(pl.Int64, strict=True))
    testset = testset.cast(pl.String)
    testset = testset.fill_null("")

    print("Read in files ....")

    for entry in range(5):
        current_string = ""
        for info in testset.row(entry):
            current_string = current_string + info + ", "
        current_string = current_string.replace(", , , , ,", ",")
        current_string = current_string.replace(", , , ,", ",")
        current_string = current_string.replace(", , ,", ",")
        current_string = current_string.replace(", ,", ",")
        if current_string.endswith(", "):
            current_string = current_string.rstrip(", ")

        tokens = Synonymes.synonymes(current_string)
        print(tokens.keys())
        results_wiki = se_wiki.search_dict(tokens)
        print(results_wiki)


if __name__ == "__main__":

    evaluate_testset_v1()
