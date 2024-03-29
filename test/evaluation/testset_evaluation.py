import polars as pl
import numpy as np

from source.HelperFunctions import find_root_directory
from source.Tokenizer import Tokenizer
from source.SearchEngine import SearchEngine
from source.EventClass import ProceedingsEvent, WikidataEvent
from source.Preprocessor import Preprocessor

import logging
import time


def evaluate_testset_v1(testset_file: str = r"../../datasets/wikidata/testset_v1.csv"):
    # initialize logging and search-engine
    root_dir = find_root_directory()

    logging.basicConfig(level=logging.INFO,
                        filename=root_dir / "logs" / "testset_v1_log.log",
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S")
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    # read-in and preprocess dataset in polars
    testset = pl.read_csv(testset_file, has_header=True, separator=';')
    pr = Preprocessor(raw_data=testset)
    pr.apply_preprocessing_pipeline(del_columns=["WikiCFP_identifier", "DBLP_identifier", "title"])
    preproc_testset = pr.get_preprocessed_data

    logging.info("Finished reading in the complete testset datafile.")

    # create tokens and apply SearchEngine
    for entry in range(100):
        current_string = ""
        for i, info in enumerate(preproc_testset.row(entry)):
            if i > 0:  # gets rid of index value for tokenization
                current_string = current_string + info + ", "
        current_string = current_string.replace(", , , , ,", ",")
        current_string = current_string.replace(", , , ,", ",")
        current_string = current_string.replace(", , ,", ",")
        current_string = current_string.replace(", ,", ",")
        if current_string.endswith(", "):
            current_string = current_string.rstrip(", ")

        try:
            tokens = Tokenizer.synonymes(current_string)
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


def evaluate_testset_v2(testset_file: str = r"../../datasets/proceedings.com/testset_v2.csv"):
    """
    Here we also try to implement the EventClasses.
    Further, we updated the testset so that it incorporates proceedings.com entries and not wikidata entries.
    This aligns with the later application.
    """
    # initialize logging and search-engine
    root_dir = find_root_directory()

    logging.basicConfig(level=logging.INFO,
                        filename=root_dir / "logs" / "testset_v2_log.log",
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S")

    # initialize SearchEngines
    se_proceedings = SearchEngine("proceedings.com", f_search=True)
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    # read-in and naively preprocess dataset in polars
    testset = pl.read_csv(testset_file, has_header=True, separator=';')
    pr = Preprocessor(raw_data=testset)
    pr.apply_preprocessing_pipeline()  # check here due to column drops and value simplification
    preproc_testset = pr.get_preprocessed_data

    logging.info("Finished reading in the complete testset datafile.")

    for entry in range(len(preproc_testset)):
        current_entry = preproc_testset.row(entry, named=True)

        # init proceedings entry, tokenizer in post_init
        proceedentry = ProceedingsEvent(input_info=current_entry)

        # apply searchengine for proceedings and wikidata datasets
        proceedhits = proceedentry.apply_searchengine(se_proceedings)
        wikihits = proceedentry.apply_searchengine(se_wiki)


# next steps:
# create new testset with proceedings.com entries (aligns with later application)
# create EventClass methods? Or other pipeline?
# build cache
