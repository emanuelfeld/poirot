# -*- codes: utf-8 -*-

from __future__ import print_function

import os
import sys
import regex
import requests
from argparse import ArgumentParser

from .filters import style
from .utils import merge_dicts


def parse_arguments(args):
        query = ArgumentParser(prog='poirot', description="""Poirot: Mind Your Language""")
        query.add_argument('--url', '-u', dest='url', default='', action="store",
            help="""The repository's git URL, e.g. 'https://github.com/dcgov/poirot.git'.""")
        query.add_argument('--dir', '-d', dest='dir', default=os.getcwd(),
            help="""The path to the local directory where the
                    git repo is located or should be stored;
                    defaults to the current directory.""")
        query.add_argument('--term', '-t', dest="term", required=False, action='store',
            help="""A single string or regular expression to search for.""")
        query.add_argument('--patterns', '-p', dest="patterns", action="store",
            help="""The path to the local file(s) containing strings
                    or regular expressions to match against, each
                    on a new line. Accepts a comma-separated list
                    of file paths.""")
        query.add_argument('--revlist', '-rl', dest='revlist', required=False, default='HEAD^!',
            help="""A comma-delimited list of revision (commit)
                    ranges to search. Defaults to HEAD^!. Specify
                    'all' to search the entire revision history.""")
        query.add_argument('--before', '-b', dest='before', required=False,
            help="""Search commits prior to a given date, e.g., Dec-12-2015""")
        query.add_argument('--after', '-a', dest='after', required=False,
            help="""Search commits after a given date, e.g., Jan-01-2015""")
        query.add_argument('--author', '-au', dest='author', required=False,
            help="""Restrict to commits made by an AUTHOR. An email
                    address is fine.""")
        query.add_argument('--staged', '-st', dest='staged', action='store_true',
            help="""Flag to search staged modifications, instead of
                    already committed ones.""")
        query.add_argument('--verbose', '-v', dest='verbose', action='store_true',
            help="""Flag to output colorful, verbose results.""")

        parsed_args = query.parse_args(args)
        formatted_args = format_arguments(parsed_args)

        return formatted_args


def parse_patterns(path):
    result = {}
    try:
        if regex.search(r'^http[s]://', path):
            r = requests.get(path)
            if r.status_code == 200:
                lines = r.text.split('\n')
            else:
                sys.exit(1)
        else:
            with open(path) as infile:
                lines = infile.readlines()
        label = None
        for line in lines:
            line = str(line).strip()
            if line.startswith('#'):
                label = line.lstrip('# ')
            elif not line:
                label = ''
            else:
                result[line] = label
    except:
        out = "Pattern file {file} does not exist.\nSpecify the correct path with --patterns".format(file=path)
        print(style(out, 'red'))
    finally:
        return result


def format_arguments(args):
    def format_revlist():
        if args.revlist == 'all':
            return ['--all']
        else:
            return [revision.strip() for revision in args.revlist.split(',')]

    def format_patterns():
        patterns = {}
        if args.term:
            patterns[args.term] = None
        try:
            file_list = [file.strip() for file in args.patterns.split(',')]
            for file in filter(lambda x: len(x), file_list):
                patterns = merge_dicts(patterns, parse_patterns(file))
        except AttributeError:
            pass
        finally:
            if not patterns:
                print(style('No patterns given! Using default pattern set.', 'blue'))
                file_dir = os.path.dirname(os.path.realpath(__file__))
                default_file = os.path.join(file_dir, 'patterns/default.txt')
                patterns = merge_dicts(patterns, parse_patterns(default_file))
            return patterns

    return {
        'before': args.before,
        'after': args.after,
        'author': args.author,
        'verbose': args.verbose,
        'dir': args.dir,
        'staged': args.staged,
        'git_dir': args.dir + '/.git',
        'repo_dir': args.dir,
        'revlist': format_revlist(),
        'git_url': args.url.rstrip('/'),
        'patterns': format_patterns()
    }
