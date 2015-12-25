import os
import sys
import argparse
import re
import subprocess
from poirot.clients.style import style


def ask(question, options, formatting=None):
    """
    Takes a question for raw_input and a set of options
    that answer the question. Bugs the user until they
    choose one of the prescribed options.

    Args:
        question: The user prompt
        options (list): The responses to choose from
        formatting: A key from style_codes in clients.style

    Returns:
        response (str): The chosen `options` item.
    """

    response = ""
    prompt = '{} [{}] '.format(question, ', '.join(options))
    while response not in options:
        response = input(style(prompt, formatting))
    return response


def merge_dicts(*dicts):
    """
    Merge an arbitrary number of dicts.

    Note:
        Updates left to right, so will override existing
        attributes!
    """

    merged = {}
    for dictionary in dicts:
        merged.update(dictionary)
    return merged


def clone_pull(git_url, repo_dir):
    """
    Clones a repository from `git_url` or optionally does a 
    git pull if the repository already exists at `repo_dir`.

    Args:
        git_url:
        repo_dir:
    """

    try:
        cmd = ['git', 'clone', git_url, repo_dir]
        subprocess.check_output(cmd, universal_newlines=True)

    except subprocess.CalledProcessError:
        response = ask('Do you want to git-pull?', ['y', 'n'], 'darkblue')
        if response == "y":
            cmd = ['git', '--git-dir=%s/.git' % (repo_dir), 'pull']
            _out = subprocess.check_output(cmd, universal_newlines=True)
            print(style('Git says: {}'.format(_out), 'smoke'))

    except:
        error = sys.exc_info()[0]
        print(style('Problem writing to destination: {}\n'.format(repo_dir), 'red'), error)
        raise


def execute_cmd(cmd):
    """
    Executes a command

    Args:
        cmd (list[str]): Command arguments
    """

    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    return popen.communicate()


def format_grep(git_dir, formatting, regex, revlist, author, before, after):
    """
    Returns a formatted git log grep command
    """

    log_cmd = ['git', '--git-dir', git_dir, 'log', revlist, '-i', '-E', '--oneline', formatting]

    if author is not None:
        log_cmd.extend(['--author', author])
    if before is not None:
        log_cmd.extend(['--before', before])
    if after is not None:
        log_cmd.extend(['--after', after])

    log_cmd.extend(regex)

    return log_cmd


def parse_metadata(log):
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
    return sha, metadata


def validate_lines(diff, line_re, pattern_re):
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
            line_num = int(re.sub(line_re, r'\1', line))
        elif line[0] == "+":
            if pattern_re.search(line):
                line_info = {"line": line_num, "text": line[1:].strip()}
                yield line_info
            line_num += 1


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
            (fname, diff_lines) = split_diff(diff, deleted_re)
            matches = [m for m in validate_lines(diff_lines, line_re, pattern_re)]
            if matches:
                files.append({"file": fname, "matches": matches})
    except TypeError:
        pass
    finally:
        return files


def split_diff(diff, deleted):
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
        if not deleted.match(diff[1]):
            filename = diff[0].split(' b/', 1)[1]
            diff = '@@' + diff[2].split('@@', 1)[1] # line numbers and diffs
            diff_lines = diff.split('\n') # split up lines
            return filename, diff_lines
    except IndexError:
        pass


def parse_pre(pattern, repo_dir):

    pattern_re = re.compile(pattern, re.I)
    deleted_re = re.compile(r'^deleted file')
    line_re = re.compile(r'@@ \-[0-9,]+ \+([0-9]+)[, ].*')

    cmd = ['git', 'diff', '--staged', '--unified=0', '--', repo_dir]
    (out, err) = execute_cmd(cmd)

    staged_diffs = parse_diff(out, pattern_re, deleted_re, line_re)

    return staged_diffs


def parse_post(ptype, pattern, git_dir, revlist=None, author=None, before=None, after=None):
    """
    Sets up and farms out the parsing of revisions' commit messages and diffs.

    Args:
        ptype: 'log' for parsing commit messages or 'diff' for actual
            file changes.
        pattern: The pattern to match against, taken from the patterns file
        revlist: A single revision or revision range
        git_dir: The local path to the repo's git directory
        author: (Optional) Authorship restriction on the revisions
        before: (Option) Date restriction on the revisions
        after: (Option) Date restriction on the revisions
    """

    if ptype == 'log':
        formatting = '--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae LOG: %s %b'
        regex = ['--grep', pattern]
    elif ptype == 'diff':        
        formatting = '--format=COMMIT: %h AUTHORDATE: %aD AUTHORNAME: %an AUTHOREMAIL: %ae'
        regex = ['-G' + pattern]

    pattern_re = re.compile(pattern, re.I)
    deleted_re = re.compile(r'^deleted file')
    line_re = re.compile(r'@@ \-[0-9,]+ \+([0-9]+)[, ].*')

    grep_cmd = format_grep(git_dir, formatting, regex, revlist, author, before, after)
    (out, err) = execute_cmd(grep_cmd)

    out = out.strip().split('COMMIT: ')
    for item in out[1:]:
        sha, metadata = parse_metadata(item)
        if ptype == 'log':
            yield sha, metadata
        else:
            show_cmd = ['git', '--git-dir', git_dir, 'show', sha, '--no-color', '--unified=0']
            (out, err) = execute_cmd(show_cmd)
            file_diffs = parse_diff(out, pattern_re, deleted_re, line_re)
            if file_diffs:
                metadata['files'] = file_diffs
                yield sha, metadata

