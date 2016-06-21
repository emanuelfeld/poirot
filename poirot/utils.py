# -*- coding: utf-8 -*-

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
        popen = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
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


def try_utf8_decode(text):
    try:
        return text.decode("utf-8")
    except AttributeError:
        return text
