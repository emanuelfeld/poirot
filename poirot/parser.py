# -*- codes: utf-8 -*-

from __future__ import print_function

import os
import sys
from argparse import ArgumentParser

import regex
import requests

from .filters import style
from .utils import merge_dicts


def parse_arguments(args):
    query = ArgumentParser(prog="poirot", description="""Poirot: Mind Your Language""")
    query.add_argument("--url", "-u", dest="url", default="", action="store",
                       help="""The repository's git URL, e.g.
                               'https://github.com/dcgov/poirot.git'.""")
    query.add_argument("--dir", "-d", dest="dir", default=os.getcwd(),
                       help="""The path to the local directory where the
                               git repo is located or should be stored;
                               defaults to the current directory.""")
    query.add_argument("--term", "-t", dest="term", required=False, action="store",
                       help="""A single string or regular expression to search for.""")
    query.add_argument("--patterns", "-p", dest="patterns", action="store",
                       help="""The path to the local file(s) containing strings
                               or regular expressions to match against, each
                               on a new line. Accepts a comma-separated list
                               of file paths.""")
    query.add_argument("--output", "-o", dest="output", required=False,
                       help="""Output results as JSON to FILE.""")
    query.add_argument("--revlist", "-rl", dest="revlist", required=False, default="HEAD^!",
                       help="""A comma-delimited list of revision (commit)
                               ranges to search. Defaults to HEAD^!. Specify
                               'all' to search the entire revision history.""")
    query.add_argument("--before", "-b", dest="before", required=False,
                       help="""Search commits prior to a given date, e.g., Dec-12-2015""")
    query.add_argument("--after", "-a", dest="after", required=False,
                       help="""Search commits after a given date, e.g., Jan-01-2015""")
    query.add_argument("--author", "-au", dest="author", required=False,
                       help="""Restrict to commits made by an AUTHOR. An email
                               address is fine.""")
    query.add_argument("--staged", "-st", dest="staged", action="store_true",
                       help="""Flag to search staged modifications, instead of
                               already committed ones.""")
    query.add_argument("--verbose", "-v", dest="verbose", action="store_true",
                       help="""Flag to output colorful, verbose results.""")

    parsed_args = query.parse_args(args)
    formatted_args = format_arguments(parsed_args)

    return formatted_args


def parse_patterns(path):
    """
    Reads in patterns from pattern file at path
    """

    result = {}
    try:
        if regex.search(r"^http[s]://", path):
            response = requests.get(path)
            if response.status_code == 200:
                lines = response.text.split("\n")
            else:
                sys.exit(1)
        else:
            with open(path) as infile:
                lines = infile.readlines()
        label = None
        for line in lines:
            line = str(line).strip()
            if line.startswith("#"):
                label = line.lstrip("# ")
            elif not line:
                label = ""
            else:
                result[line] = label
    except:
        out = """Pattern file {file} does not exist.\n
                 Specify the correct path with --patterns""".format(file=path)
        print(style(out, "red"))
    return result


def format_arguments(args):
    """Cleans up arguments passed to argparse"""

    def format_revlist():
        if args.revlist == "all":
            return ["--all"]
        else:
            return [revision.strip() for revision in args.revlist.split(",")]

    def format_patterns():
        patterns = {}
        if args.term:
            patterns[args.term] = None
        try:
            file_list = [path.strip() for path in args.patterns.split(",") if path.strip()]
            for path in file_list:
                patterns = merge_dicts(patterns, parse_patterns(path))
        except AttributeError:
            pass
        if not patterns:
            print("No patterns given! Using default pattern set.")
            file_dir = os.path.dirname(os.path.realpath(__file__))
            default_file = os.path.join(file_dir, "patterns/default.txt")
            patterns = merge_dicts(patterns, parse_patterns(default_file))
        return patterns

    return {
        "before": args.before,
        "after": args.after,
        "author": args.author,
        "verbose": args.verbose,
        "dir": args.dir,
        "staged": args.staged,
        "git_dir": args.dir + "/.git",
        "repo_dir": args.dir,
        "revlist": format_revlist(),
        "git_url": args.url.rstrip("/"),
        "patterns": format_patterns(),
        "output": args.output
    }
