import argparse
import os
import time
import re

from poirot.helpers import clone_pull, merge_dicts, parse_git
from poirot.clients.style import style

VERSION = '0.1.0'


class Poirot(object):

    def __init__(self, client, case):
        """
        Poirot needs to know who he's working for (client) and
        the details of the case. He also likes to get things in
        order by setting up a place to store findings that match
        key patterns.

        Args:
            client: ConsoleClient or ConsoleClientThin object
            case: Case object
        """

        self.meta = {'date': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                     'version': VERSION}
        self.client = client
        self.case = case
        self.findings = {p: {} for p in case.patterns}

    def prepare(self):
        """
        Before conducting his investigation, Poirot must work out
        what events (revisions) to consider. He will then gather
        (clone, pull, or locate) the information to go through.
        """

        case = self.case

        if case.skip:
            print(style('Skipping clone or pull as --skip was found', 'blue'))
            if not os.path.exists(case.git_dir):
                raise IOError('Invalid .git directory: {}\nSpecify '
                              'the correct local directory with '
                              '--dest'.format(case.git_dir))
        else:
            clone_pull(case.git_url, case.repo_dir)

    def investigate(self):
        """
        Set up and initiate parsing of revisions
        in the given list of individual revisions
        or revision subsets, for the patterns
        provided.
        """

        case = self.case

        try:
            revisions = case.revlist.strip().split(',')
        except AttributeError:
            revisions = []

        for pattern in case.patterns:
            for revision in revisions:
                parser_args = {
                    "git_dir": case.git_dir,
                    "revlist": revision,
                    "author": case.author,
                    "before": case.before,
                    "after": case.after
                }
                self.parse('log', pattern, parser_args)
                self.parse('diff', pattern, parser_args)

    def parse(self, item_type, pattern, parser_args):
        """
        Call commit log and diff parsers on a revision
        or revision subset and add matching commit logs
        and diffs to findings.
        """
        finding = self.findings[pattern]

        for commit, metadata in parse_git(item_type, pattern, **parser_args):
            if not hasattr(finding, commit):
                finding[commit] = {}
            finding[commit] = merge_dicts(finding[commit], metadata)

    def report(self):
        """Render findings in the console"""
        self.client.render(self.findings, self.case.__dict__)
        # pass


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
        self.skip = facts.skip
        self.dest = facts.dest

        self.git_url = facts.url.rstrip('/')
        self.repo_url = re.sub(r'\.git$', '', self.git_url)

        repo = self.git_url.rsplit('/', 1)[1]
        repo_name = re.sub(r'\.git$', '', repo)

        self.repo_dir = '{}/{}'.format(self.dest, repo_name)
        self.git_dir = self.repo_dir + '/.git'

        if facts.revlist == 'all':
            self.revlist = '--all'
        elif facts.revlist is None:
            self.revlist = 'HEAD^!'
        else:
            self.revlist = facts.revlist

        self.patterns = set()
        if facts.term:
            self.patterns.add(facts.term)

        pfile_list = facts.patterns.strip().split(',')
        for pfile in pfile_list:
            file_patterns = set([p for p in self.add_patterns(pfile)])
            self.patterns.update(file_patterns)

    def add_patterns(self, file_path):
        """
        Args:
            file_path: Path to a file with patterns separated by newlines.

        Yields:
            line: A line in the pattern file that is neither blank, nor
                commented out.
        """

        try:
            with open(file_path) as infile:
                for line in infile:
                    line = line.rstrip()
                    if line and not line.startswith('#'):
                        yield line
        except IOError:
            raise IOError('Pattern file {} does not exist.\nSpecify '
                          'the correct file path with '
                          '--patterns'.format(file_path))

    def parser(self, _dir=os.path.dirname(__file__),
               _patterns='patterns/default.txt',
               _temp='../temp'):

        query = argparse.ArgumentParser(prog="poirot",
                                        description="Poirot: Mind Your PII")
        query.add_argument('--url', '-u',
                           dest="url",
                           required=True,
                           action="store",
                           help="The fully qualified git URL.")
        query.add_argument('--dest', '-d',
                           dest="dest",
                           default=os.path.join(_dir, _temp),
                           help="""Path to the local directory where the
                                git repo is located or should be stored.
                                Default: clouseau/temp""")
        query.add_argument('--term', '-t',
                           dest="term",
                           required=False,
                           action="store",
                           help="Search for a single regular expression.")
        query.add_argument('--patterns', '-p',
                           dest="patterns",
                           action="store",
                           default=os.path.join(_dir, _patterns),
                           help="""Path to .txt file containing regular expressions
                                to match against, each on a new line.
                                Accepts a comma-separated list of file
                                paths.""")
        query.add_argument('--revlist', '-rl',
                           dest="revlist",
                           required=False,
                           help="""A comma-delimited list of revisions (commits)
                                to search. Defaults to HEAD^!. Specify 'all'
                                to search the entire revision history.""")
        query.add_argument('--before', '-b',
                           dest='before',
                           required=False,
                           help="""Search commits prior to a given date,
                                e.g., Dec-12-2015""")
        query.add_argument('--after', '-a',
                           dest="after",
                           required=False,
                           help="""Search commits after a given date,
                                e.g., Jan-01-2015""")
        query.add_argument('--author',
                           dest="author",
                           required=False,
                           help="""Restrict to commits made by AUTHOR. An email
                                address is fine.""")
        query.add_argument('--skip', '-s',
                           dest="skip",
                           action="store_true",
                           help="""If specified, skips any calls to git-clone or
                                git-pull. Useful in combination with --dest to
                                test a local git repo""")
        return query
