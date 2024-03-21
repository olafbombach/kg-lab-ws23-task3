from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter


def find_root_directory(marker_file: str = ".git") -> Path:
    """
    The idea of this function is to define a marker-file that we can search in the current directory.

    If we do not find it in the file directory, we proceed to the parent of the file.
    If we find the file, then we can be sure, that we are in the root directory path of the project.

    Default for marker_file: '.git', since this file is part of the root repository.
    """
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / marker_file).exists():
            return current_path
        else:
            current_path = current_path.parent


def get_arg_parser(description: str) -> ArgumentParser:
    """
    Setup command line argument parser.
    """
    parser = ArgumentParser(prog='esc',
                            description=description,
                            formatter_class=RawTextHelpFormatter)
    # add arguments
    parser.add_argument("operation",
                        choices=["small_test", "v2", "full", "resources"],
                        help="Define the operation being performed.")
    parser.add_argument("--s_measure",
                        choices=["euc", "cos"],
                        default="euc",
                        help="Determine the similarity measure to compare the encodings. \n Default: \"euc\"")    
    parser.add_argument("--encoding",
                        choices=["bert", "glove"],
                        default="bert",
                        help="Determine the encoding technique being applied to the signatures. \n Default: \"bert\"")

    return parser
