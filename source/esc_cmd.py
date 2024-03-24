import sys
import os
import logging
import polars as pl
from nicegui import ui
import subprocess

from source.HelperFunctions import find_root_directory, get_arg_parser
from source.EventClass import ProceedingsEvent

from source.Downloader import Downloader
from source.Preprocessor import Preprocessor
from source.SearchEngine import SearchEngine
from source.Comparor import Comparor
from source.WikidataUpdater import WikidataUpdater


def download_resources() -> None:
    """
    Download all resources to the directory datasets.
    Further distinguishes between Glove already being downloaded or not.
    """
    path_to_check = find_root_directory() / "datasets" / "glove"

    if len(os.listdir(path_to_check)) <= 1:  # due to .gitignore
        Downloader.download_all()
    else:
        Downloader.update_datasets()


def evaluation_v2(sim_measure: str, encoding: str, small_test: bool=False) -> None:
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
        filename = root_dir / "results" / "logs" / f"small_test_{encoding}_{sim_measure}.log"
    else:
        filename = root_dir / "results" / "logs" / f"testset_v2_{encoding}_{sim_measure}.log"
    
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s - %(message)s",
                                  datefmt="%m/%d/%Y %I:%M:%S")

    process_logger = logging.getLogger('process_logger')
    process_logger.setLevel(logging.INFO)
    process_handler = logging.FileHandler(filename, mode='w')
    process_handler.setFormatter(formatter)
    process_logger.addHandler(process_handler)

    console_logger = logging.getLogger('console_logger')
    console_logger.setLevel(logging.WARNING)
    console_handler = logging.StreamHandler()
    console_logger.addHandler(console_handler)
    
    # start with the code
    try:
        se_wiki = SearchEngine("Wikidata", f_search=True)
    except FileNotFoundError:
        raise FileNotFoundError("Please make sure that you downloaded all the necessary data. \n"
                                "Check \"esc resources\" or \"scripts/resources.sh\".")
    except Exception as e:
        raise Exception("Unexpected error due to: ", e)

    process_logger.info("Start reading and preprocessing the testset datafile.")

    testset = pl.read_csv(testset_file, has_header=True, separator=";")
    pr = Preprocessor(raw_data=testset)
    pr.apply_preprocessing_pipeline(testset=True)
    preproc_testset = pr.get_preprocessed_data

    process_logger.info("Finished reading in the complete testset datafile.")

    # create tokens and apply SearchEngine
    for i, entry in enumerate(preproc_testset.iter_rows(named=True)):
        pe = ProceedingsEvent(input_info=entry)

        # searching of events
        loe = pe.apply_searchengine(se_instance=se_wiki, max_search_hits=10)
        process_logger.info(f"Found {len(loe)} wikidata entries for this proceedings.com entry.")
        
        # semantification of events
        process_logger.info("Semantification of entries started.")
        dict_file_pe = pe.apply_semantifier(get_signatures=True)
        loe.apply_semantifier(logger=process_logger, get_signatures=True)  # dict saved as class attribute 

        # get key-configurations for the encodings
        loe.compute_configurations(pe=pe)

        # encoding events
        process_logger.info("Semantification finished. Moving on to encoding...")
        pe.apply_encoder(dict_file=dict_file_pe, encoding=encoding)
        loe.apply_encoder(encoding=encoding)

        # comparing events
        process_logger.info("Encoding finished...")
        co = Comparor(pe=pe, loe=loe)
        co.add_measure_as_attribute(sim_measure)

        # get optimal value and receive decision
        opt_event = co.get_optimal_similarity(metric=sim_measure)
        decision = co.case_decision(metric=sim_measure)
        process_logger.info(f"{opt_event.similarity:.3f} -> {decision}")

        # presentation of fit
        process_logger.info("Finding optimal value for the following ProceedingsEvent:")
        process_logger.info(pe)
        process_logger.info("Optimal WikidataEvent for ProceedingsEvent:")
        process_logger.info(opt_event)
        process_logger.info(f"Real / True labeling: {entry['wikidata_index']}")

        print(f"Finished {i+1}. iteration.")
        
        if small_test:  # only one item for small test
            break

        del pe, loe

    del se_wiki, testset, preproc_testset

def full_pipeline(sim_measure: str, encoding: str) -> None:
    """
    Full pipeline to find matches between proceedings.com events and Wikidata events.
    Depending on the outcome creates an entry.
    """
    print("Start reading in dataset...")
    root_dir = find_root_directory()
    file_dir = root_dir / "datasets" / "proceedings.com"
    all_files = os.listdir(file_dir)
    
    try:
        # this assumes that there exist one and only one excel-file in this dir
        excel_file = [f for f in all_files if f.startswith('all-') and f.endswith('.xlsx')][0]
    except IndexError:
        raise FileNotFoundError("Please make sure that you downloaded all the necessary data. \n"
                                "Check \"esc resources\" or \"scripts/resources.sh\".")
    except Exception as e:
        raise Exception("Unexpected error due to: ", e)

    # set up logger
    process_log_filename = root_dir / "results" / "logs" / f"full_{encoding}_{sim_measure}.log"
    history_filename = root_dir / "results" / "logs" / f"history.log"
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s - %(message)s",
                                  datefmt="%m/%d/%Y %I:%M:%S")

    process_logger = logging.getLogger('process_logger')
    process_logger.setLevel(logging.INFO)
    process_handler = logging.FileHandler(process_log_filename, mode='w')
    process_handler.setFormatter(formatter)
    process_logger.addHandler(process_handler)

    history_logger = logging.getLogger('history_logger')
    history_logger.setLevel(logging.INFO)
    history_handler = logging.FileHandler(history_filename, mode='a')
    history_logger.addHandler(history_handler)

    console_logger = logging.getLogger('console_logger')
    console_logger.setLevel(logging.WARNING)
    console_handler = logging.StreamHandler()
    console_logger.addHandler(console_handler)
    
    # start with the code
    se_wiki = SearchEngine("Wikidata", f_search=True)

    process_logger.info("Start reading and preprocessing the datafile.")

    dataset = pl.read_excel(file_dir / excel_file, engine="openpyxl")
    pr = Preprocessor(raw_data=dataset)
    deletion_columns = ["Editor", "Pages", "Format", "POD Publisher", "Series",
                        "Publ Year", "Subject2", "Subject3", "Subject4", 
                        "List Price"]
    pr.apply_preprocessing_pipeline(testset=False, del_columns=deletion_columns)
    preproc_dataset = pr.get_preprocessed_data

    print("Start iteration...")
    process_logger.info("Finished reading and preprocessing the complete datafile.")

    # get previous history
    with open(history_filename, mode="r") as f:
        history = f.readlines()
        history = [num.replace("\n", "") for num in history]

    # start iteration
    for i, entry in enumerate(preproc_dataset.iter_rows(named=True)):
        # logic if proceedings.com entry already has been uploaded!
        current_isbn = entry.get("ISBN")  # isbn as unique identifier for proceedings.com
        if current_isbn in history:
            process_logger.info(f"Proceedings.com event {current_isbn} was already used in this pipeline. Moving on to the next...")
            continue
        else:
            pass

        pe = ProceedingsEvent(input_info=entry)

        # searching of events
        loe = pe.apply_searchengine(se_instance=se_wiki, max_search_hits=10)
        process_logger.info(f"Found {len(loe)} wikidata entries for this proceedings.com entry.")
        
        # semantification of events
        process_logger.info("Semantification of entries started.")
        dict_file_pe = pe.apply_semantifier(get_signatures=True)
        loe.apply_semantifier(logger=process_logger, get_signatures=True)  # dict saved as class attribute 

        # get key-configurations for the encodings
        loe.compute_configurations(pe=pe)

        # encoding events
        process_logger.info("Semantification finished. Moving on to encoding...")
        pe.apply_encoder(dict_file=dict_file_pe, encoding=encoding)
        loe.apply_encoder(encoding=encoding)

        # comparing events
        process_logger.info("Encoding finished...")
        co = Comparor(pe=pe, loe=loe)
        co.add_measure_as_attribute(sim_measure)

        # get optimal value and receive decision
        opt_event = co.get_optimal_similarity(metric=sim_measure)
        decision = co.case_decision(metric=sim_measure)
        process_logger.info(f"{opt_event.similarity:.3f} -> {decision}")

        co.result_to_json()

        # presentation of fit
        process_logger.info("Finding optimal value for the following ProceedingsEvent:")
        process_logger.info(pe)
        
        process_logger.info("Optimal WikidataEvent for ProceedingsEvent:")
        try:
            process_logger.info(opt_event)
        except UnicodeEncodeError as e:
            process_logger.info("Visualization of Wikidata event omitted due to {e}.")

        print(f"Finished {i+1}. iteration for entry {current_isbn}. Went to -> {decision}")
        history_logger.info(current_isbn)
        history.append(current_isbn)
        
        del pe, loe, co, decision, opt_event, dict_file_pe, current_isbn

    del se_wiki, dataset, preproc_testset

def resolve_unclear_entries():
    """
    Start GUI for visualization of unclear entries. 
    Manual resolving necessary.
    """
    # I know this is not how you should do it, but I did not see another way...
    subprocess.run(['venv/Scripts/python', 'source/Gui.py'])

def upload_entries():
    """
    Upload all found and unfound entries that can be found in the json files of
    \"results/\" to Wikidata. 
    """
    
    wu_found = WikidataUpdater(found=True)
    wu_found.update_all_entries()
    del wu_found

    wu_unfound = WikidataUpdater(found=False)
    wu_unfound.update_all_entries()
    del wu_unfound


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

    # logic
    if args.operation == "small_test":
        print("Please check the directory results/logs to find your small_test run.")
        evaluation_v2(sim_measure=args.s_measure, encoding=args.encoding, small_test=True)

    elif args.operation == "v2":
        print("Please check the directory results/logs to find your run.")
        evaluation_v2(sim_measure=args.s_measure, encoding=args.encoding, small_test=False)

    elif args.operation == "full":
        print("Please check the directory results/logs to find your run.")
        full_pipeline(sim_measure=args.s_measure, encoding=args.encoding)

    elif args.operation == "solve":
        print("Start GUI...")
        resolve_unclear_entries()

    elif args.operation == "upload":
        print("Will upload or update the found new entries to Wikidata...")
        try:
            upload_entries()
        except FileNotFoundError:
            raise FileNotFoundError("First make sure that you generate data using the full_pipeline. \n\"esc full\"")
        except Exception as e:
            raise e("Unexpected error due to: ", e)

    elif args.operation == "resources":
        print("Downloading all necessary files:")
        download_resources()

