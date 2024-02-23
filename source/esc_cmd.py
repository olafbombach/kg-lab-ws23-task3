import sys
import logging
import polars as pl

from source.HelperFunctions import find_root_directory
from source.HelperFunctions import get_arg_parser, get_last_commit_time
from source.EventClass import WikidataEvent, ProceedingsEvent

from source.Preprocessor import Preprocessor
from source.SearchEngine import SearchEngine



def evaluation_v1() -> None:
    """
    This function evaluates the search operation using the Tokenizer
    and the SearchEngine.
    It consists of Wikidata entries that are tokenized and further searched
    in the complete database of Wikidata.
    If the correct ID can be refound within a specified range of results (def: 5),
    it is classified as TP. Else it is a false example.
    Also returns a log in \"results/logs\".
    """
    
    root_dir = find_root_directory()
    testset_file = root_dir/"datasets"/"wikidata"/"testset_v1.csv"

    # set up logger
    logging.basicConfig(level=logging.INFO,
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S")
    
    file_handler = logging.FileHandler(filename=root_dir/"results"/"logs"/"testset_v1_log.log")

    logging.getLogger('').addHandler(file_handler)
    
    # start with the code
    se_wiki = SearchEngine("Wikidata", f_search=True)

    logging.info("Start reading and preprocessing the testset datafile.")

    testset = pl.read_csv(testset_file, has_header=True, separator=";")
    pr = Preprocessor(raw_data=testset)
    pr.apply_preprocessing_pipeline(del_columns=["WikiCFP_identifier", "DBLP_identifier", "title"])
    preproc_testset = pr.get_preprocessed_data

    logging.info("Finished reading in the complete testset datafile.")

    # create tokens and apply SearchEngine
    for i, entry in enumerate(preproc_testset.iter_rows(named=True)):
        wd = WikidataEvent(input_info=entry)
        loe = wd.apply_searchengine(se_wiki)
        print(len(loe))
        del wd, loe
        if i > 5:
            break

    del se_wiki, testset, preproc_testset


def evaluation_v2() -> None:
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
    logging.basicConfig(level=logging.INFO,
                        filemode="w",
                        format="%(asctime)s %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S",
                        filename=root_dir/"results"/"logs"/"testset_v2_log.log")
    
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
        loe = pe.apply_searchengine(se_instance=se_wiki)
        logging.info(f"Found {len(loe)} wikidata entries for this proceedings.com entry.")
        
        logging.info("Semantification of entries started.")
        dict_file_pe = pe.apply_semantifier(get_dict=True)
        loe.apply_semantifier(get_list=True)

        logging.info("Semantification finished. Moving on to encoding...")
        pe.apply_encoder(dict_file_pe)
        loe.apply_encoder()

        logging.info("Encoding finished. Writing to log:")
        logging.info("The proceedings.com entry:")
        logging.info(pe)
        logging.info("The List of Events (Wikidata) as outcomes:")
        logging.info(loe)
        print(f"Finished {i+1}. iteration.")

        del pe, loe

        if i > 4:
            break

    del se_wiki, testset, preproc_testset


def main():
    """ main program """

    program_short_name = "esc"
    program_build_date = get_last_commit_time()
    program_description = f"Program for Event Series Completion. \n"\
                          f"Different operations are possible.\n" \
                          f"\n"\
                          f"Maintainers: Efe Bilgili, Christophe Haag, " \
                          f"Lukas Jaeschke, Daniel Quirmbach \n" \
                          f"Last update: {program_build_date}"

    try:
        parser = get_arg_parser(description=program_description)
        args = parser.parse_args()
        if len(vars(args)) < 1:
            parser.print_usage()
            sys.exit(0)
    except KeyboardInterrupt:
        # handle keyboard interrupt
        return sys.exit(0)

    # dummy
    if args.operation == "v1":
        print("You have chosen v1-evaluation. Still not working...")
    elif args.operation == "v2":
        evaluation_v2()
