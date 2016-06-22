# -*- codes: utf-8 -*-

from __future__ import print_function

import sys
import json

import regex
from tqdm import tqdm

from .filters import style
from .utils import clone_pull, execute_cmd, is_git_dir, utf8_decode
from .parser import parse_arguments
from .clients import render


def main(args=sys.argv[1:], render_results=True, skip_clone_pull=False):
    investigator = Poirot(args, render_results, skip_clone_pull)

    for pattern in tqdm(investigator.info["patterns"]):
        investigator.search(utf8_decode(pattern))

    return investigator.get_results()


class Poirot(object):
    def __init__(self, args, render_results=True, skip_clone_pull=True):
        self.render_results = render_results
        self.info = parse_arguments(args)
        self.results = {utf8_decode(p): {} for p in self.info["patterns"]}

        if self.info["staged"]:
            is_git_dir(self.info["git_dir"])
        elif self.info["git_url"] and not skip_clone_pull:
            clone_pull(self.info["git_url"], self.info["repo_dir"])


    def search(self, pattern):
        """
        Delegates to add_staged_results or add_committed_results
        """

        if self.info["staged"]:
            self.add_staged_results(pattern)
        else:
            self.add_committed_results(pattern)


    def add_staged_results(self, pattern):
        """
        Adds staged matches to results
        """

        result = self.search_staged(pattern)
        self.results[pattern] = {"staged": {"files": result}} if result else {}


    def search_staged(self, pattern):
        """
        Takes a text pattern and local repo directory and returns the
        file name, line number, and text matching the given pattern in
        a staged revision.
        """

        cmd = ["git", "diff", "--staged", "--unified=0", "--",
               self.info["repo_dir"]]
        (out, err) = execute_cmd(cmd)
        return self.parse_diff(diff=out, pattern=pattern)


    def add_committed_results(self, pattern):
        """
        Adds committed matches (logs, messages) to results
        """

        def merge_committed(target, commit_range):
            """
            Reads in yielded commit sha and pattern match information from
            search_committed. Adds to pattern matches for for the particular
            commit.
            """

            for commit, metadata in self.search_committed(target, pattern, commit_range):
                self.results[pattern].setdefault(commit, {}).update(metadata)

        for commit_range in self.info["revlist"]:
            merge_committed("diff", commit_range)
            merge_committed("message", commit_range)


    def search_committed(self, target, pattern, commit_range):
        """
        Searches within a range of commits for commit messages or diffs
        containing the text pattern. Yields a matching revision's SHA
        and the message or file name, line number, text matching the
        given pattern, and authorship.
        """

        for log in self.get_logs(target, pattern, commit_range):
            sha, metadata = self.parse_log(log)
            if target == "message":
                yield sha, metadata
            else:
                # show the diffs for a given commit
                cmd = ["git", "--git-dir", self.info["git_dir"],
                       "show", sha, "--no-color", "--unified=0"]
                (out, err) = execute_cmd(cmd)
                file_diffs = self.parse_diff(diff=out, pattern=pattern)
                if file_diffs:
                    metadata["files"] = file_diffs
                    yield sha, metadata


    def get_logs(self, target, pattern, commit_range):
        """
        Searches and returns git logs in a range of revisions that match a
        specified pattern, either in the message or modified lines.
        """

        cmd = ["git", "--git-dir", self.info["git_dir"], "log",
               commit_range, "-i", "-E", "--oneline"]

        if target == "message":
            cmd.extend(["--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae LOG: %s %b"])
            cmd.extend(["--grep", pattern])  # limits matching to the log message
        elif target == "diff":
            cmd.extend(["--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae"])
            cmd.extend(["-G" + pattern])  # matches on added/removed lines

        if self.info["author"]:
            cmd.extend(["--author", self.info["author"]])
        if self.info["before"]:
            cmd.extend(["--before", self.info["before"]])
        if self.info["after"]:
            cmd.extend(["--after", self.info["after"]])

        (out, err) = execute_cmd(cmd)
        return out.strip().split("COMMIT: ")[1:]


    @staticmethod
    def parse_log(log):
        """
        Parses the information contained in a pretty-formatted
        --oneline commit log (i.e. the commit SHA, author's
        name and email, the date the commit was authored, and,
        optionally, the commit's message).
        """

        metadata = {}
        sha, log = log.split(" AUTHORDATE: ", 1)
        metadata["author_date"], log = log.split(" AUTHORNAME: ", 1)
        metadata["author_name"], log = log.split(" AUTHOREMAIL: ", 1)
        try:
            metadata["author_email"], metadata["message"] = log.split(" LOG: ", 1)
            metadata["message"] = utf8_decode(metadata["message"])
        except ValueError:
            metadata["author_email"] = log
        metadata = {key: metadata[key].strip() for key in metadata.keys()}
        return sha, metadata


    @staticmethod
    def parse_diff(diff, pattern):
        """
        Takes a single commit's diff and pattern. Returns the files
        and lines in the revision that match the pattern.
        """

        def split_diff(diff):
            """
            Divides a diff into the file name and the rest of its
            (split by newline).
            """

            deleted_re = regex.compile(r"^deleted file")

            try:
                diff = diff.split("\n", 2)
                if not deleted_re.match(diff[1]):
                    filename = diff[0].split(" b/", 1)[1]
                    diff = "@@" + diff[2].split("@@", 1)[1]
                    diff_text = diff.split("\n")
                    return filename, diff_text
            except IndexError:
                pass

        def find_matches_in_diff(diff_text):
            """
            Takes the lines from a file's diff and yields them
            if they were added and match the given pattern.
            """

            line_re = regex.compile(r"@@ \-[0-9,]+ \+([0-9]+)[, ].*")
            pattern_re = regex.compile(pattern, regex.I)
            line_num = 0
            for line in diff_text:
                line = utf8_decode(line)
                if not line:
                    pass
                elif line[0] == "@":
                    line_num = int(regex.sub(line_re, r"\1", line))
                elif line[0] == "+":
                    if pattern_re.search(line):
                        yield {"line": line_num, "text": line[1:].strip()}
                    line_num += 1

        try:
            if isinstance(diff, bytes):
                diff = diff.decode()  # coerce bytes type to str
        except:
            pass

        files = []
        file_diffs = diff.split("diff --git ")[1:]  # split the diff by file modified

        for file_diff in file_diffs:
            try:
                (filename, diff_text) = split_diff(file_diff)
                matches = [m for m in find_matches_in_diff(diff_text)]
                if matches:
                    files.append({"file": filename, "matches": matches})
            except TypeError:  # ignore empty lines
                pass
        return files


    def get_results(self):

        if self.info["output"]:
            with open(self.info["output"], "w") as outfile:
                json.dump(self.results, outfile, ensure_ascii=False, indent=4)

        if not self.render_results:
            return self.results

        if any(self.results.values()):
            render(self.results, self.info)
            sys.exit(1)
        else:
            print(style("Poirot didn't find anything!", "darkblue"))
            sys.exit(0)
