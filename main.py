import sys
import webbrowser

from googlesearch import search
from termcolor import colored

import utils
from parser_factory import ParserFactory
from terminal_printer import TerminalPrinter
from utils import build_google_link
from utils_objects import Site, Thread

sites_to_search = [Site.SOF]


def menu_open_answer_in_web(thread):
    """
    Opens the thread in the user's browsers
    """
    if thread:
        webbrowser.open(thread.url)
    else:
        print("No more threads for this query, try searching edit the query using 'e'")


def menu_next_answer_in_thread(thread: Thread, answer_idx):
    """
    Prints the next answer in the thread, returns True if such answer exists, other False
    """
    if thread and answer_idx < len(thread.answers):
        TerminalPrinter.print_answer(thread.answers[answer_idx])
        return True
    return False


def menu_open_google_in_web(query):
    """
    Opens the google search page on the given query in the user's browsers
    """
    webbrowser.open(build_google_link(query))


def get_results_generator(site, query):
    """
    Return a generator of results(Threads) of the given site to the given query
    """
    query = "site: {} {}".format(site.url, query)
    TerminalPrinter.print_query(query)
    search_generator = search(query)
    return search_generator


def all_sites_results_generator(site_generators):
    """
    A general generator of threads to all given site generators
    """
    for site in site_generators:
        for result in site:
            yield result
    while (True):
        yield None


def menu_update_query(run_args):
    """
    Asks the user for input a new query, updates the run_args given dict
    """
    run_args['command'] = input("input command:")
    run_args['error'] = input("input error:")
    run_args['query'] = utils.get_query(run_args['command'], run_args['error'])


def run(run_args):
    """
    Runs the main menu loop according to the given run_args dict
    """
    site_parsers = ParserFactory.generate_parser_objects(sites_to_search)
    query = run_args['query']
    site_results_generators = [
        parser.parse_links(get_results_generator(parser.site.value, run_args['query']))
        for parser in site_parsers]
    results_generator = all_sites_results_generator(site_results_generators)
    curr_result = next(results_generator)
    answer_idx = 0
    if curr_result:
        TerminalPrinter.print_question(curr_result)
        if menu_next_answer_in_thread(curr_result, answer_idx):
            answer_idx += 1
        else:
            print("No more answers in this thread..")
    else:
        print("No more threads for this query..\nEnter 'e' to edit your query")
    while (True):
        # what do you want to do?
        user_input = input(colored("please choose next action (input {} for help)", "green").format("'h'"))
        if user_input == "h":
            TerminalPrinter.print_help_menu()
        elif user_input == "na":
            if menu_next_answer_in_thread(curr_result, answer_idx):
                answer_idx += 1
            else:
                print("No more answers in this thread..\nEnter 'n' for next thread")
        elif user_input == "n":
            curr_result = next(results_generator)
            if curr_result:
                TerminalPrinter.print_question(curr_result)
                answer_idx = 0
                if menu_next_answer_in_thread(curr_result, answer_idx):
                    answer_idx += 1
                else:
                    print("No more answers in this thread..\nEnter 'n' for next thread")
            else:
                print("No more threads for this query..\nEnter 'e' to edit your query")
        elif user_input == "o":
            menu_open_answer_in_web(curr_result)
        elif user_input == "g":
            menu_open_google_in_web(query)
        elif user_input == "cmd":
            print(run_args.get('command', query))
        elif user_input == "err":
            print(run_args.get('error', query))
        elif user_input == "e":
            menu_update_query(run_args)
            return run_args
        elif user_input == "x":
            exit(0)


if __name__ == '__main__':
    run_args = {}
    if sys.argv[1] == 'h':
        print("Run Examples:\nwww --q [query to search]\nwww [command to run]")
        exit()
    elif sys.argv[1] == 'e':
        menu_update_query(run_args)
    elif sys.argv[1] == "q":
        run_args['query'] = " ".join(sys.argv[2:])
    else:
        run_args = utils.get_run_info(sys.argv)
        run_args['query'] = utils.get_query(run_args['command'], run_args['error'])
    while (True):
        run(run_args)
