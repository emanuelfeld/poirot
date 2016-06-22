# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import subprocess

from .filters import style


def ask(question, options, response=None, formatting=None):
    """
    Takes a question for raw_input and a set/list of options
    that answer the question. Prompts the user until they
    choose one of the prescribed options.

    Args:
        question: The user prompt
        options (list): The responses to choose from
        formatting: A key from style_codes in clients.style

    Returns:
        response (str): The chosen `options` item.
    """

    get_input = input
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input
    prompt = "{} [{}] ".format(question, ", ".join(options))
    while response not in options:
        response = get_input(style(prompt, formatting))
    return response


def merge_dicts(*dicts):
    """
    Merges an arbitrary number of dicts.

    Note:
        Updates left to right, so will override existing
        attributes!
    """

    merged = {}
    for dictionary in dicts:
        merged.update(dictionary)
    return merged


def execute_cmd(cmd):
    """
    Executes a command and returns the stdout and stderr.
    """

    try:
        popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                 universal_newlines=True)
        (out, err) = popen.communicate()
    except UnicodeDecodeError:
        popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = popen.communicate()
        try:
            out = out.decode("latin-1")
            out = out.encode("utf-8")
        except:
            error = sys.exc_info()[0]
            print(style("There was a problem executing command: {}\n".format(cmd), "red"), error)
            out = ""
    return (out, err)


def utf8_decode(text):
    try:
        return text.decode("utf-8")
    except AttributeError:
        return text


def is_git_dir(directory):
    # checks that command invoked on a git directory
    if not os.path.exists(directory):
        raise IOError("""Invalid .git directory: {directory}\nSpecify
                      the correct local directory with
                      --dir""".format(directory=directory))

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
