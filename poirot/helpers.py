import os
import sys
import argparse
import re
import subprocess
from clients.style import style


def ask(question, options, formatting=None):
    """
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
        response = raw_input(style(prompt, formatting))
    return response


def clone_pull(git_url, repo_dir):
    """
    Clones a repository from `git_url` or optionally does a 
    git pull if the repository already exists at `repo_dir`.

    Args:
        git_url:
        repo_dir:
    """

    try:
        subprocess.check_output(['git', 'clone', git_url, repo_dir])

    except subprocess.CalledProcessError:
        print style('Directory {} exits.'.format(repo_dir), 'blue')
        response = ask('Do you want to git-pull?', ['y', 'n'], 'red')
        if response == "y":
            _out = subprocess.check_output(['git', '--git-dir={}/.git'.format(repo_dir), 'pull'])
            print style('Git says: {}'.format(_out), 'smoke')

    except:
        error = sys.exc_info()[0]
        print style('Problem writing to destination: {}'.format(repo_dir), 'red'), error
        raise


def execute_cmd(cmd):
    """
    Executes a (git) command

    Args:
        cmd (list[str]): Git arguments
    """

    popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return popen.communicate()


# Grep search a git directory revision range
def format_grep(git_dir, formatting, regex, revlist='HEAD\^\!', author=None, before=None, after=None):
    """
    Returns a formatted git log grep command
    """

    log_cmd = ['git', '--git-dir', git_dir, 'log', revlist, '-i', '-E', '--oneline', formatting]

    if author is not None:
        log_cmd.append('--author')
        log_cmd.append(author)
    if before is not None:
        log_cmd.append('--before')
        log_cmd.append(before)
    if after is not None:
        log_cmd.append('--after')
        log_cmd.append(after)
    if revlist == 'all':
        log_cmd[4] = '--all'
    log_cmd.extend(regex)

    return log_cmd


def inspect_revision(git_dir, commit, pattern_re, deleted_re, line_re):
    """
    Args:
        git_dir:
        commit:
        pattern_re:
        deleted_re:
        line_re:

    Returns:
        files:
    """

    files = []
    show_cmd = ['git', '--git-dir', git_dir, 'show', commit, '--no-color', '--unified=0']
    (out, err) = execute_cmd(show_cmd)

    try:
        diff_list = out.split('diff --git ')[1:]
        for diff in diff_list:
            (fname, diff_lines) = split_commit(diff, deleted_re)
            matches = [m for m in match_lines(diff_lines, line_re, pattern_re)]
            if matches:
                files.append({"file": fname, "matches": matches})
    except:
        pass
    return files


def split_commit(diff, deleted):
    """
    Args:
        diff: A single file's unified diff information
        deleted: Compiled regex matching deleted files

    Returns:
        If the file was not deleted in the revision:

        fname (str): The file's name
        diff_lines (list[str]): Lines modified in `diff`.
    """

    diff = diff.split('\n', 2)
    if not deleted.match(diff[1]):
        fname = diff[0] # filename
        diff = '@@' + diff[2].split('@@', 1)[1] # line numbers and diffs
        diff_lines = diff.split('\n') # split up lines
        return fname, diff_lines


def match_lines(diff, line_re, pattern_re):
    """
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


def parse_commits(git_dir, pattern, revlist, author, before, after):
    """
    Args:
        git_dir:
        pattern:
        revlist:
        author:
        before:
        after:
    """

    matches = []
    formatting = '--format=%H'
    regex = ['-G' + pattern]

    grep_cmd = format_grep(git_dir, formatting, regex, revlist, author, before, after)
    (out, err) = execute_cmd(grep_cmd)

    revisions = out.strip().split('\n')

    pattern_re = re.compile(pattern, re.I)
    deleted_re = re.compile(r'^deleted file')
    line_re = re.compile(r'@@ \-[0-9,]+ \+([0-9]+)[, ].*')

    for revision in revisions:
        match = {revision: {"files": []}}
        files = inspect_revision(git_dir, revision, pattern_re, deleted_re, line_re)
        if files:
            yield revision, files


def parse_logs(git_dir, pattern, revlist, author, before, after):
    """
    Args:
        git_dir:
        pattern:
        revlist:
        author:
        before:
        after:
    """

    matches = []
    formatting = '--format=COMMIT: %H %s %b'
    regex = ['--grep', pattern]

    grep_cmd = format_grep(git_dir, formatting, regex, revlist, author, before, after)
    (out, err) = execute_cmd(grep_cmd)
    print out
    try:
        out = out.strip().split('COMMIT: ')
        for log in out[1:]:
            log = log[1:-1].split(' ', 1)
            commit = log[0]
            message = log[1]
            yield commit, message
    except:
        pass
