from __future__ import print_function

import os
import regex
import sys

from .helpers import ask, merge_dicts, execute_cmd
from .style import style
from .parser import parse_arguments
from .clients import render


def main(args=sys.argv, render_results=True):
    args.pop(0)
    info = parse_arguments(args)
    results = {}
    if not os.path.exists(info['git_dir']):
        raise IOError('Invalid .git directory: {dir}\nSpecify '
                      'the correct local directory with '
                      '--dir'.format(dir=info['git_dir']))
    if info['staged']:
        print(style('Investigating staged revisions', 'blue'))
        for pattern in info['patterns']:
            result = parse_pre(pattern, info['repo_dir'])
            results[pattern] = {'staged': {'files': result}} if result else {}
    else:
        if info['git_url']:
            clone_pull(info['git_url'], info['repo_dir'])
        for pattern in info['patterns']:
            results[pattern] = {}
            for revision in info['revlist']:
                merge_post('diff', pattern, revision, info, results)
                merge_post('message', pattern, revision, info, results)
    if not render_results:
        return results
    found_evidence = any(len(f) for f in results.values())
    if found_evidence:
        render(results, info)
        sys.exit(1)
    else:
        print(style("Poirot didn't find anything!", 'darkblue'))
        sys.exit(0)


def merge_post(item_type, pattern, revision, info, results):
    for commit, metadata in parse_post(item_type, pattern, revision, info):
        if not hasattr(results[pattern], commit):
            results[pattern][commit] = {}
        results[pattern][commit] = merge_dicts(results[pattern][commit], metadata)
    return results


def clone_pull(git_url, repo_dir):
    """
    Clones a repository from `git_url` or optionally does a 
    git pull if the repository already exists at `repo_dir`.
    """

    try:
        cmd = ['git', 'clone', git_url, repo_dir]
        subprocess.check_output(cmd, universal_newlines=True)

    except subprocess.CalledProcessError:
        response = ask('Do you want to git-pull?', ['y', 'n'], 'darkblue')
        if response == "y":
            cmd = ['git', '--git-dir=%s/.git' % (repo_dir), 'pull']
            out = subprocess.check_output(cmd, universal_newlines=True)
            print(style('Git says: {}'.format(out), 'smoke'))

    except:
        error = sys.exc_info()[0]
        print(style('Problem writing to destination: {}\n'.format(repo_dir), 'red'), error)
        raise


def parse_pre(pattern, repo_dir):
    """
    Takes a text pattern and local repo directory and returns the file name,
    line number, and text matching the given pattern in a staged revision.

    Args:
        pattern: A single text pattern to search for.
        repo_dir: The local path the repo's base directory.
    """
    pattern_re = regex.compile(pattern, regex.I)
    deleted_re = regex.compile(r'^deleted file')
    line_re = regex.compile(r'@@ \-[0-9,]+ \+([0-9]+)[, ].*')

    cmd = ['git', 'diff', '--staged', '--unified=0', '--', repo_dir]
    (out, err) = execute_cmd(cmd)

    staged_diffs = parse_diff(out, pattern_re, deleted_re, line_re)

    return staged_diffs


def parse_post(target, pattern, revlist, info):
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

    pattern_re = regex.compile(r'{}'.format(pattern), regex.I)
    deleted_re = regex.compile(r'^deleted file')
    line_re = regex.compile(r'@@ \-[0-9,]+ \+([0-9]+)[, ].*')

    out = get_matching_revisions(target, pattern, revlist, info)

    for item in out:
        sha, metadata = parse_log_metadata(item)
        if target == 'message':
            yield sha, metadata
        else:
            show_cmd = ['git', '--git-dir', info['git_dir'], 'show', sha, '--no-color', '--unified=0']
            (out, err) = execute_cmd(show_cmd)
            file_diffs = parse_diff(out, pattern_re, deleted_re, line_re)
            if file_diffs:
                metadata['files'] = file_diffs
                yield sha, metadata


def get_matching_revisions(target, pattern, revlist, info):

    cmd = ['git', '--git-dir', info['git_dir'], 'log', revlist, '-i', '-E', '--oneline']

    if target == 'message':
        cmd.extend(['--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae LOG: %s %b'])
        cmd.extend(['--grep', pattern])
    elif target == 'diff':        
        cmd.extend(['--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae'])
        cmd.extend(['-G' + pattern])

    if info['author'] is not None:
        cmd.extend(['--author', info['author']])
    if info['before'] is not None:
        cmd.extend(['--before', info['before']])
    if info['after'] is not None:
        cmd.extend(['--after', info['after']])

    (out, err) = execute_cmd(cmd)
    out = out.strip().split('COMMIT: ')[1:]
    return out


def parse_log_metadata(log):
    """
    Parses the information contained in a pretty-formatted
    --oneline commit log (i.e. the commit SHA, author's
    name and email, the date the commit was authored, and,
    optionally, the commit's message).

    Args:
        log (str): oneline pretty-formatted git log output

    Returns:
        commit (str): the revision's abbreviated SHA value.
        metadata (dict): author name, email, date (and maybe
            commit message).
    """

    metadata = {}
    sha, log = log.split(' AUTHORDATE: ', 1)
    metadata["author_date"], log = log.split(' AUTHORNAME: ', 1)
    metadata["author_name"], log = log.split(' AUTHOREMAIL: ', 1)
    try:
        metadata["author_email"], metadata["log"] = log.split(' LOG: ', 1)
    except ValueError:
        metadata["author_email"] = log
    metadata = {key: metadata[key].strip() for key in metadata.keys()}
    return sha, metadata


def parse_diff(text, pattern_re, deleted_re, line_re):
    """
    Takes a single revision and pattern. Returns the files and lines
    in the revision that match the pattern.

    Args:
        git_dir: Path to the repo's git directory.
        commit: A single revision's SHA.
        pattern_re: Compiled pattern regex.
        deleted_re: Compiled regex matching file deletions.
        line_re: Compiled regex matching line number metadata.

    Returns:
        files (list[dict]): A list of dictionaries containing the
            name of a file and any matching lines, with their text
            and line number.
    """

    files = []
    try:
        diff_list = text.split('diff --git ')[1:]
        for diff in diff_list:
            (filename, lines) = split_diff(diff, deleted_re)
            matches = [m for m in parse_diff_lines(lines, line_re, pattern_re)]
            if matches:
                files.append({"file": filename, "matches": matches})
    except TypeError:
        pass
    finally:
        return files


def split_diff(diff, deleted_re):
    """
    Divides a diff into the file name and the rest of its
    (split by newline).

    Args:
        diff: A single file's unified diff information
        deleted: Compiled regex matching deleted files

    Returns:
        If the file was not deleted in the revision:

        fname (str): The file's name
        diff_lines (list[str]): Lines modified in `diff`.
    """

    try:
        diff = diff.split('\n', 2)
        if not deleted_re.match(diff[1]):
            filename = diff[0].split(' b/', 1)[1]
            diff = '@@' + diff[2].split('@@', 1)[1]
            diff_lines = diff.split('\n')
            return filename, diff_lines
    except IndexError:
        pass


def parse_diff_lines(diff, line_re, pattern_re):
    """
    Takes the lines from a file's diff and yields them
    if they were added.

    Args:
        diff: A single file's unified diff information.
        line_re: Compiled regex matching line number information.
        pattern_re: Compiled regex matching a given pattern.

    Yields:
        line_info: A dictionary for a line where additions were made
            and which includes pattern_re. Contains the line's number
            and text.
    """

    line_num = 0
    for line in diff:
        if not line:
            pass
        elif line[0] == "@":
            line_num = int(regex.sub(line_re, r'\1', line))
        elif line[0] == "+":
            if pattern_re.search(line):
                yield {"line": line_num, "text": line[1:].strip()}
            line_num += 1