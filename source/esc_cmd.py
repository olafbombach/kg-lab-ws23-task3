import sys
import pathlib
from source.HelperFunctions import get_arg_parser, get_last_commit_time


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
        print("You have chosen v1-evaluation.")
    elif args.operation == "v2":
        print("You have chosen v2-evaluation.")
