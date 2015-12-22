import time
import re
import os
import argparse
from clients import *
from helpers import parse_commits, clone_pull
from clients.style import style


class Poirot(object):

    def __init__(self, client, case, investigation):
        """
        Args:
            client: ConsoleClient or ConsoleClientThin object
            case: Case object
            investigation: Investigation object
        """
        self.meta = {'date': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
        self.case = case
        self.investigation = investigation
        self.client = client

    def prepare(self):
        """
        Optionally clone or pull the case's git repo
        """

        if self.case.skip:
            print style('Skipping clone or pull as --skip was found', 'blue')
        else:
            clone_pull(self.case.git_url, self.case.repo_dir)

    def investigate(self):
        """
        Call commit log and diff parsers on the given list of
        individual revisions or revision ranges.
        """
        revisions = []
        case = self.case
        if case.revlist:
            revisions = case.revlist.strip().split(',')
        for pattern in case.patterns:
            for revision in revisions:
                commit_matches = parse_commits(revision, case.git_dir, pattern, case.author, case.before, case.after)
                if commit_matches:
                    self.investigation.add_matches(pattern, commit_matches)
        #         message_matches = parse_messages(revision,
        #             self.case.git_dir, pattern)
        #         self.investigation.add_matches(pattern, message_matches)

    def report(self):
        self.client.render(self.case.patterns, self.investigation.findings, self.case.__dict__)


class Case(object):

    def __init__(self, testimony):
        parser = self.get_input()
        facts = parser.parse_args(testimony)

        self.patterns = set()

        pfile_list = facts.patterns.strip().split(',')
        for pfile in pfile_list:
            file_patterns = set([p for p in self.add_patterns(pfile)])
            self.patterns.update(file_patterns)

        self.dest = facts.dest
        self.git_url = facts.url.rstrip('/')

        repo = self.git_url.rsplit('/', 1)[1]
        repo_name = re.sub(r'\.git$', '', repo)

        self.repo_dir = '{}/{}'.format(self.dest, repo_name)
        self.git_dir = self.repo_dir + '/.git'
        self.clean = facts.clean
        self.revlist = facts.revlist
        self.term = facts.term
        self.before = facts.before
        self.after = facts.after
        self.author = facts.author
        self.skip = facts.skip

    def add_patterns(self, file_path):
        with open(file_path) as infile:
            for line in infile:
                line = line.rstrip()
                if line and not line.startswith('#'):
                    yield line

    def get_input(self, _dir=os.path.dirname(__file__),
                  _patterns='patterns/default.txt',
                  _temp='../temp'):

        query = argparse.ArgumentParser(prog="poirot",
                                        description="Poirot: Mind Your PII")
        query.add_argument('--url', '-u',
                           dest="url",
                           required=True,
                           action="store",
                           help="The fully qualified git URL.")
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
        query.add_argument('--clean', '-c',
                           dest="clean",
                           action="store_true",
                           default=False,
                           help="Delete the existing git repo and re-clone")
        query.add_argument('--dest', '-d',
                           dest="dest",
                           default=os.path.join(_dir, _temp),
                           help="""Path to the local directory where the
                                git repo is located or should be stored.
                                Default: clouseau/temp""")
        query.add_argument('--revlist', '-rl',
                           dest="revlist",
                           required=False,
                           help="""A comma-delimited list of revisions (commits) to search.
                                Defaults to HEAD^!. Specify 'all' to search the entire
                                revision history.""")
        query.add_argument('--before', '-b',
                           dest='before',
                           required=False,
                           help="""Search commits prior to a given date,
                                e.g., Mar-08-2013""")
        query.add_argument('--after', '-a',
                           dest="after",
                           required=False,
                           help="""Search commits after a given date,
                                e.g., Mar-10-2013""")
        query.add_argument('--author',
                           dest="author",
                           required=False,
                           help="Restrict to commits made by AUTHOR. An email address is fine.")
        query.add_argument('--skip', '-s',
                           dest="skip",
                           action="store_true",
                           help="If specified, skips any calls to git-clone or git-pull. Useful in combination with --dest to test a local git repo")
        return query


class Investigation(object):

    def __init__(self):
        self.findings = {}

    def add_matches(self, pattern, matches):
        try:
            self.findings[pattern].extend(matches)
        except KeyError:
            self.findings[pattern] = matches
