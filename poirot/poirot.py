# -*- codes: utf-8 -*-

from __future__ import print_function

import os
import subprocess
import sys
import json

import regex
from tqdm import tqdm

from .filters import style
from .utils import ask, execute_cmd, merge_dicts, try_utf8_decode
from .parser import parse_arguments
from .clients import render


def main(args=sys.argv, render_results=True):
    info = parse_arguments(args)
    results = {}

    def is_git_dir(dir):
        # checks that command invoked on a git directory
        if not os.path.exists(dir):
            raise IOError("""Invalid .git directory: {dir}\nSpecify
                          the correct local directory with 
                          --dir""".format(dir=dir))

    # searches staged changes
    if info["staged"]:
        is_git_dir(info["git_dir"])
        print(style("Investigating staged revisions", "blue"))
        for pattern in info["patterns"]:
            pattern = try_utf8_decode(pattern)
            result = search_staged(pattern, info["repo_dir"])
            results[pattern] = {"staged": {"files": result}} if result else {}

    # searches commit diffs and logs
    else:
        if info["git_url"]:
            clone_pull(info["git_url"], info["repo_dir"])
        for pattern in tqdm(info["patterns"]):
            pattern = try_utf8_decode(pattern)
            results[pattern] = {}
            for revision in info["revlist"]:
                merge_committed("diff", pattern, revision, info, results)
                merge_committed("message", pattern, revision, info, results)


    # output results to JSON file
    if info["output"]:
        with open(info["output"], "w") as outfile:
            json.dump(results, outfile, ensure_ascii=False, indent=4)

    if not render_results:
        return results
    # render results in console if any pattern matches found
    elif any(results.values()):
        render(results, info)
        sys.exit(1)
    else:
        print(style("Poirot didn't find anything!", "darkblue"))
        sys.exit(0)


def merge_committed(target, pattern, revision, info, results):
    """
    Reads in yielded commit sha and match information from search_committed.
    Adds to pattern matches for for the particular commit.
    """

    for commit, metadata in search_committed(target, pattern, revision, info):
        if not hasattr(results[pattern], commit):
            results[pattern][commit] = {}
        results[pattern][commit] = merge_dicts(results[pattern][commit], metadata)
    return results


def clone_pull(git_url, repo_dir):
    """
    Clones a repository from `git_url` or optionally does a
    git pull if the repository already exists at `repo_dir`.
    Runs only if url argument provided to poirot command.
    """
    try:
        cmd = ["git", "clone", git_url, repo_dir]
        subprocess.check_output(cmd, universal_newlines=True)

    except subprocess.CalledProcessError:
        response = ask("Do you want to git-pull?", ["y", "n"], "darkblue")
        if response == "y":
            cmd = ["git", "--git-dir=%s/.git" % (repo_dir), "pull"]
            out = subprocess.check_output(cmd, universal_newlines=True)
            print(style("Git says: {}".format(out), "smoke"))

    except:
        error = sys.exc_info()[0]
        print(style("Problem writing to destination: {}\n".format(repo_dir), "red"), error)
        raise


def search_staged(pattern, repo_dir):
    """
    Takes a text pattern and local repo directory and returns the file name,
    line number, and text matching the given pattern in a staged revision.

    Args:
        pattern: A single text pattern to search for.
        repo_dir: The local path the repo"s base directory.
    """

    cmd = ["git", "diff", "--staged", "--unified=0", "--", repo_dir]

    (out, err) = execute_cmd(cmd)
    result = parse_diff(diff=out, pattern=pattern)

    return result


def search_committed(target, pattern, revlist, info):
    """
    Takes restrictions on the elements of the revision history (message or diff)
    to search and yields a matching revision's SHA and the message or file name,
    line number, and text matching the given pattern, as well as its authorship.

    Args:
        target: The revision component being grep searched ('message' or 'diff').
        pattern: A single text pattern to search for.
        revlist: The revision or revision range to be searched.
        info: Parsed arguments

    Yields:
        sha: The SHA or a revision matching the search.
        metadata: The matching revision message or line number and text, and Authorship
            information.
    """

    logs = get_logs(target, pattern, revlist, info)

    for log in logs:
        sha, metadata = parse_log(log)
        if target == "message":
            yield sha, metadata
        else:
            # show the diffs for a given commit
            cmd = ["git", "--git-dir", info["git_dir"], "show", sha, "--no-color", "--unified=0"]
            (out, err) = execute_cmd(cmd)
            file_diffs = parse_diff(diff=out, pattern=pattern)
            if file_diffs:
                metadata["files"] = file_diffs
                yield sha, metadata


def get_logs(target, pattern, revlist, info):
    """
    Searches and returns git logs in a range of revisions that match a specified pattern,
    either in the message or modified lines.
    """

    cmd = ["git", "--git-dir", info["git_dir"], "log", revlist, "-i", "-E", "--oneline"]

    if target == "message":
        cmd.extend(["--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae LOG: %s %b"])
        cmd.extend(["--grep", pattern])  # limits matching to the log message
    elif target == "diff":
        cmd.extend(["--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae"])
        cmd.extend(["-G" + pattern])  # matches on added/removed lines

    if info["author"]:
        cmd.extend(["--author", info["author"]])
    if info["before"]:
        cmd.extend(["--before", info["before"]])
    if info["after"]:
        cmd.extend(["--after", info["after"]])

    (out, err) = execute_cmd(cmd)
    return out.strip().split("COMMIT: ")[1:]


def parse_log(log):
    """
    Parses the information contained in a pretty-formatted
    --oneline commit log (i.e. the commit SHA, author's
    name and email, the date the commit was authored, and,
    optionally, the commit's message).

    Args:
        log (str): oneline pretty-formatted git log output

    Returns:
        commit (str): the revision's abbreviated SHA value.
        metadata (dict): author name, email, date (and
            commit message, if there is one).
    """

    metadata = {}
    sha, log = log.split(" AUTHORDATE: ", 1)
    metadata["author_date"], log = log.split(" AUTHORNAME: ", 1)
    metadata["author_name"], log = log.split(" AUTHOREMAIL: ", 1)
    try:
        metadata["author_email"], metadata["log"] = log.split(" LOG: ", 1)
        metadata["log"] = try_utf8_decode(metadata["log"])
    except ValueError:
        metadata["author_email"] = log
    metadata = {key: metadata[key].strip() for key in metadata.keys()}
    return sha, metadata


def parse_diff(diff, pattern):
    """
    Takes a single commit's diff and pattern. Returns the files
    and lines in the revision that match the pattern.

    Args:
        diff: The log message and textual diff.
        pattern: The pattern being searched for.

    Returns:
        files (list[dict]): A list of dictionaries containing the
            name of a file and any matching lines, with their text
            and line number.
    """

    files = []
    try:
        if isinstance(diff, bytes):
            diff = diff.decode()  # sometimes a diff will come back in bytes type, so coerce to str
    except:
        pass
    file_diffs = diff.split("diff --git ")[1:]  # split the diff by file modified
    for file_diff in file_diffs:
        try:
            (filename, diff_text) = split_diff(file_diff)
            matches = [m for m in find_matches_in_diff(diff_text, pattern)]
            if matches:
                files.append({"file": filename, "matches": matches})
        except TypeError:  # ignore empty lines
            pass
    return files


def split_diff(diff):
    """
    Divides a diff into the file name and the rest of its
    (split by newline).

    Args:
        diff: A single file's unified diff information

    Returns:
        If the file was not deleted in the revision:

        fname (str): The file's name
        diff_text (list[str]): Lines modified in `diff`.
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


def find_matches_in_diff(diff_text, pattern):
    """
    Takes the lines from a file's diff and yields them
    if they were added and match the given pattern.

    Args:
        diff_text: A single file's unified diff information.
        pattern: The pattern being searched for.

    Yields:
        A dictionary for a line where additions were made
        and which includes pattern_re. Contains the line's number
        and text.
    """

    line_re = regex.compile(r"@@ \-[0-9,]+ \+([0-9]+)[, ].*")
    pattern_re = regex.compile(pattern, regex.I)
    line_num = 0
    for line in diff_text:
        line = try_utf8_decode(line)
        if not line:
            pass
        elif line[0] == "@":
            line_num = int(regex.sub(line_re, r"\1", line))
        elif line[0] == "+":
            if pattern_re.search(line):
                yield {"line": line_num, "text": line[1:].strip()}
            line_num += 1
