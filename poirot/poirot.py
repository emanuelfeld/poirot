from __future__ import print_function

import argparse
import os
import regex
import sys
from tqdm import tqdm

from .helpers import clone_pull, merge_dicts, parse_post, parse_pre
from .style import style
from .clients import ConsoleClient, ConsoleThinClient


class Poirot(object):

    def __init__(self, case):
        """
        Poirot needs to know who he's working for (client) and
        the details of the case. He also likes to get things in
        order by setting up a place to store findings that match
        key patterns.

        Args:
            client: ConsoleClient or ConsoleClientThin object
            case: Case object
        """

        self.case = case
        self.findings = {p: {} for p in case.patterns}

    def prepare(self):
        """
        Before conducting his investigation, Poirot must work out
        what events (revisions) to consider. He will then gather
        (clone, pull, or locate) the information to go through.
        """

        case = self.case

        if case.staged:
            print(style('Investigating staged revisions', 'blue'))

        if case.git_url:
            clone_pull(case.git_url, case.repo_dir)
        else:
            print(style('Investigating local revisions', 'blue'))
            if not os.path.exists(case.git_dir):
                raise IOError('Invalid .git directory: {}\nSpecify '
                              'the correct local directory with '
                              '--dir'.format(case.git_dir))

    def investigate(self):
        """
        Set up and initiate parsing of revisions
        in the given list of individual revisions
        or revision subsets, for the patterns
        provided.
        """

        case = self.case

        if case.staged:
            for p in case.patterns:
                self.findings[p] = parse_pre(p, case.repo_dir)

        else:
            for pattern in tqdm(case.patterns):
                for revision in case.revlist:
                    parser_args = {
                        'git_dir': case.git_dir,
                        'revlist': revision,
                        'author': case.author,
                        'before': case.before,
                        'after': case.after
                    }
                    self.parse_post('message', pattern, parser_args)
                    self.parse_post('diff', pattern, parser_args)

    def parse_post(self, item_type, pattern, parser_args):
        """
        Call commit log and diff parsers on a revision
        or revision subset and add matching commit logs
        and diffs to findings.
        """

        finding = self.findings[pattern]

        for commit, metadata in parse_post(item_type, pattern, **parser_args):
            if not hasattr(finding, commit):
                finding[commit] = {}
            finding[commit] = merge_dicts(finding[commit], metadata)

    def report(self):
        """Render findings in the console"""

        found_evidence = any(f for f in self.findings.values())
        if found_evidence:
            if self.case.verbose:
                self.client = ConsoleClient()
            else:
                self.client = ConsoleThinClient()
            self.client.render(data=self.findings, info=self.case.__dict__)
            sys.exit(1)
        else:
            print(style("Poirot didn't find anything!", 'darkblue'))
            sys.exit(0)


class Case(object):

    def __init__(self, args):
        """
        Sometimes the facts of a case come jumbled. Poirot sorts
        them out.
        """

        facts = self.parser().parse_args(args)

        self.before = facts.before
        self.after = facts.after
        self.author = facts.author
        self.staged = facts.staged
        self.verbose = facts.verbose

        self.git_url = facts.url.rstrip('/')
        self.repo_url = regex.sub(r'\.git$', '', self.git_url)
        self.repo_dir = facts.dir
        self.git_dir = facts.dir + '/.git'

        if facts.revlist == 'all':
            self.revlist = ['--all']
        else:
            self.revlist = facts.revlist.strip().split(',')

        self.patterns = set()
        if facts.term:
            self.patterns.add(facts.term)

        try:
            pfile_list = facts.patterns.strip().split(',')
            pfile_list = [pfile for pfile in pfile_list if pfile]
            for pfile in pfile_list:
                file_patterns = set([p for p in self.add_patterns(pfile)])
                self.patterns.update(file_patterns)
        except AttributeError:
            pass

        if len(self.patterns) == 0:
            print(style('No patterns given! Using default pattern set.', 'blue'))
            pattern_path = os.path.dirname(os.path.realpath(__file__))
            pattern_path = os.path.join(pattern_path, 'patterns/default.txt')
            file_patterns = set([p for p in self.add_patterns(pattern_path)])
            self.patterns.update(file_patterns)

    def add_patterns(self, file_path):
        """
        Takes a pattern file's path and yields its patterns
        """

        try:
            with open(file_path) as infile:
                for line in infile:
                    line = line.rstrip()
                    if line and not line.startswith('#'):
                        yield line
        except (IOError, OSError):
            warning = "Pattern file {} does not exist. "\
                      "Specify the correct file path with --patterns".format(file_path)
            print(style(warning, 'red'))

    def parser(self):
        query = argparse.ArgumentParser(prog='poirot', description="""Poirot:
                                        Mind Your Language""")
        query.add_argument('--url', '-u',
                           dest='url',
                           default='',
                           action="store",
                           help="""The repository's git URL,
                                e.g. 'https://github.com/dcgov/poirot.git'.""")
        query.add_argument('--dir', '-d',
                           dest='dir',
                           default=os.getcwd(),
                           help="""The path to the local directory where the
                                git repo is located or should be stored;
                                defaults to the current directory.""")
        query.add_argument('--term', '-t',
                           dest="term",
                           required=False,
                           action='store',
                           help="""A single string or regular expression
                                to search for.""")
        query.add_argument('--patterns', '-p',
                           dest="patterns",
                           action="store",
                           default=False,
                           help="""The path to the local file(s) containing strings
                                or regular expressions to match against, each
                                on a new line. Accepts a comma-separated list
                                of file paths.""")
        query.add_argument('--revlist', '-rl',
                           dest='revlist',
                           required=False,
                           default='HEAD^!',
                           help="""A comma-delimited list of revision (commit)
                                ranges to search. Defaults to HEAD^!. Specify
                                'all' to search the entire revision
                                history.""")
        query.add_argument('--before', '-b',
                           dest='before',
                           required=False,
                           help="""Search commits prior to a given date,
                                e.g., Dec-12-2015""")
        query.add_argument('--after', '-a',
                           dest='after',
                           required=False,
                           help="""Search commits after a given date,
                                e.g., Jan-01-2015""")
        query.add_argument('--author', '-au',
                           dest='author',
                           required=False,
                           help="""Restrict to commits made by an AUTHOR. An email
                                address is fine.""")
        query.add_argument('--staged', '-st',
                           dest='staged',
                           action='store_true',
                           help="""Flag to search staged modifications, instead of
                                already committed ones.""")
        query.add_argument('--verbose', '-v',
                           dest='verbose',
                           action='store_true',
                           help="""Flag to output colorful, verbose results.""")
        return query
