import sys
import logging
import polars as pl

from source.HelperFunctions import find_root_directory
from source.HelperFunctions import get_arg_parser
from source.EventClass import WikidataEvent, ProceedingsEvent

from source.Preprocessor import Preprocessor
from source.SearchEngine import SearchEngine
from source.Comparor import Comparor



def evaluation_v2(sim_measure: str, small_test: bool=False) -> None:
    """
    This function evaluates operation using the Tokenizer, the SearchEngine, 
    the Semantifier and the Encoding.
    The testset consists of proceedings.com entries that are tokenized 
    and further searched in the complete database of Wikidata.
    
    Also returns a log in \"results/logs\".
    """
    root_dir = find_root_directory()
    testset_file = root_dir/"datasets"/"proceedings.com"/"testset_v2.csv"

    # set up logger
    if small_test:
        logging.basicConfig(level=logging.INFO,
                            filemode="w",
                            format="%(asctime)s %(levelname)s - %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S",
                            filename=root_dir/"results"/"logs"/f"small_test_{sim_measure}.log")
    else:
        logging.basicConfig(level=logging.INFO,
                            filemode="w",
                            format="%(asctime)s %(levelname)s - %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S",
                            filename=root_dir/"results"/"logs"/f"testset_v2_{sim_measure}_new_new.log")
    
    # start with the code
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    testset = pl.read_csv(testset_file, has_header=True, separator=";")
    pr = Preprocessor(raw_data=testset)
    pr.apply_preprocessing_pipeline()
    preproc_testset = pr.get_preprocessed_data

    logging.info("Finished reading in the complete testset datafile.")

    # create tokens and apply SearchEngine
    for i, entry in enumerate(preproc_testset.iter_rows(named=True)):
        pe = ProceedingsEvent(input_info=entry)

        # searching of events
        loe = pe.apply_searchengine(se_instance=se_wiki, max_search_hits=20)
        logging.info(f"Found {len(loe)} wikidata entries for this proceedings.com entry.")
        
        # semantification of events
        logging.info("Semantification of entries started.")
        dict_file_pe = pe.apply_semantifier(get_dict=True)
        loe.apply_semantifier(get_dict=True)  # dict saved as class attribute 

        # get key-configurations for the encodings!
        loe.compute_configurations(pe=pe)

        # encoding events
        logging.info("Semantification finished. Moving on to encoding...")
        pe.apply_encoder(dict_file = dict_file_pe)
        loe.apply_encoder()

        # comparing events
        logging.info("Encoding finished...")
        co = Comparor(pe=pe, loe=loe)
        co.add_measure_as_attribute(sim_measure)

        # get optimal value and receive decision
        opt_event = co.get_optimal_similarity(metric=sim_measure)
        decision = co.case_decision(metric=sim_measure)
        logging.info(f"{opt_event.similarity:.3f} -> {decision}")

        # further processing
        if decision == "Unfound":
            pass
        elif decision == "Unclear":
            pass
        elif decision == "Found":
            pass
        else:
            print("This should not happen...")

        # presentation of fit
        logging.info("Finding optimal value for the following ProceedingsEvent:")
        logging.info(pe)
        logging.info("Optimal WikidataEvent for ProceedingsEvent:")
        logging.info(opt_event)
        logging.info(f"Real / True labeling: {entry['wikidata_index']}")

        print(f"Finished {i+1}. iteration.")
        
        if small_test:  # only one item for small test
            break

        del pe, loe

    del se_wiki, testset, preproc_testset


def main():
    """ main program """

    program_description = f"Program for Event Series Completion. \n"\
                          f"Different operations are possible.\n" \
                          f"\n"\
                          f"Maintainers: Efe Bilgili, Christophe Haag, " \
                          f"Lukas Jaeschke, Daniel Quirmbach"

    try:
        parser = get_arg_parser(description=program_description)
        args = parser.parse_args()
        if len(vars(args)) < 1:
            parser.print_usage()
            sys.exit(0)
    except KeyboardInterrupt:
        # handle keyboard interrupt
        print("Keyboard interruption was triggered.")
        return sys.exit(0)

    # dummy
    if args.operation == "small_test":
        print("Please check the directory results/logs to find your small_test run.")
        evaluation_v2(sim_measure=args.s_measure, small_test=True)
    elif args.operation == "v2":
        print("Please check the directory results/logs to find your run.")
        evaluation_v2(sim_measure=args.s_measure)

