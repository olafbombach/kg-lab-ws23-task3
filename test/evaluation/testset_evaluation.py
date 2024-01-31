import time

from source.synonymes import Synonymes
from source.data_search_opt import SearchEngine
from source.Evaluator import Evaluator
from source.EventClass import TokenSet, ProceedingsEvent, WikidataEvent

import logging
import polars as pl
import numpy as np


def evaluate_testset_v1(testset_file: str = r"../../datasets/wikidata/testset_v1_opt.csv"):
    # initialize logging and search-engine
    logging.basicConfig(level=logging.INFO,
                        filename="log/eval_log_1.log",
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S")
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    # read-in and preprocess dataset in polars
    testset = pl.read_csv(testset_file, has_header=True, separator=';')
    testset = testset.drop("WikiCFP_identifier", "DBLP_identifier", "title")  # no index needed
    testset = testset.with_columns(pl.col('beginnings').cast(pl.Int64, strict=True))
    testset = testset.cast(pl.String)
    testset = testset.fill_null("")

    logging.info("Finished reading in the complete testset datafile.")

    # create tokens and apply SearchEngine
    for entry in range(100):
        current_string = ""
        for i, info in enumerate(testset.row(entry)):
            if i > 0:  # gets rid of index value for tokenization
                current_string = current_string + info + ", "
        current_string = current_string.replace(", , , , ,", ",")
        current_string = current_string.replace(", , , ,", ",")
        current_string = current_string.replace(", , ,", ",")
        current_string = current_string.replace(", ,", ",")
        if current_string.endswith(", "):
            current_string = current_string.rstrip(", ")

        try:
            tokens = Synonymes.synonymes(current_string)
            results_wiki = se_wiki.search_dict(tokens)

            # evaluation part
            correct_index = int(testset.row(entry)[0])
            found_indices = [int(index) for index in results_wiki["index"].to_list()]

            if correct_index in found_indices:
                position = np.where(np.array(found_indices) == correct_index)[0][0]
                logging.info(f"index {int(testset.row(entry)[0])}: Success! "
                            f"Result: position {position+1} of {len(found_indices)}")
                del position, correct_index, found_indices
            else:
                logging.error(f"index {int(testset.row(entry)[0])}: Fail!")

            del tokens, results_wiki

        except (ValueError, pl.exceptions.ComputeError):
            logging.critical(f"index {testset.row(entry)[0]}: Mayor problem occurred while performing.")


def evaluate_testset_v2(testset_file: str = r"../../datasets/wikidata/testset_v1_opt.csv"):
    """
    Here we also try to implement the EventClasses.
    Further, we updated the testset so that it incorporates proceedings.com entries and not wikidata entries.
    This aligns with the later application.
    """
    # initialize logging and search-engine
    logging.basicConfig(level=logging.INFO,
                        filename="log/eval_log_2.log",
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S")
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    # read-in and preprocess dataset in polars
    testset = pl.read_csv(testset_file, has_header=True, separator=';')
    testset = testset.drop("WikiCFP_identifier", "DBLP_identifier", "title")  # hier nochmal überarbeiten
    testset = testset.with_columns(pl.col('beginnings').cast(pl.Int64, strict=True))  # hier nochmal überarbeiten
    testset = testset.cast(pl.String)
    testset = testset.fill_null("")

    logging.info("Finished reading in the complete testset datafile.")

    for entry in range(5):
        current_entry = testset.row(entry)
        print(type(current_entry))

    proceedingsentry = ProceedingsEvent(input_info=current_entry)

# next steps:
# sort out the problems of the tokenizer since it can create "(..." which is suboptimal for regex-method
# create new definition where I also include semantification and encoding
# build cache


if __name__ == "__main__":

    evaluate_testset_v1()
