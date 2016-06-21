# -*- coding: utf-8 -*-

import regex

PREFIX = "\033["
RESET = PREFIX + "0m"

STYLE_CODES = {
    "bold": "1m",
    "gray": "1;30m",
    "black": "30m",
    "red": "1;31m",
    "darkred": "31m",
    "green": "1;32m",
    "darkgreen": "32m",
    "yellow": "1;33m",
    "brown": "33m",
    "blue": "1;34m",
    "darkblue": "34m",
    "fuscia": "1;35m",
    "purple": "35m",
    "cyan": "1;36m",
    "darkcyan": "36m",
    "white": "1;37m",
    "smoke": "37m",
    "default": "39m",
    "yellow_bg": "43m",
    "cyan_bg": "46m",
    "blue_bg": "42m",
    "orange_bg": "41m",
    "white_bg": "47m",
    "default_bg": "49m"
}

for code in STYLE_CODES:
    STYLE_CODES[code] = PREFIX + STYLE_CODES[code]

SYMBOL_CODES = {
    "ok": u"\u2713",
    "fail": u"\u2716",
}


def style(text, _code):
    """Takes a string and styles its print output"""

    try:
        return "%s%s%s" % (STYLE_CODES[_code], text, RESET)
    except:
        return "%s" % (text)


def ok(text):
    """Takes a string and prepends a green check to it"""

    return "%s %s" % (style(SYMBOL_CODES["ok"], "green"), text)


def fail(text=""):
    """Takes a string and prepends a red x mark to it"""

    return "%s %s" % (style(SYMBOL_CODES["fail"], "red"), text)


def highlight(text, pattern):
    """Takes a string and highlights substrings matching a pattern"""

    pattern_re = regex.compile(pattern, regex.I)
    match = pattern_re.search(text)
    if match:
        text = text.replace(match.group(0), style(match.group(0), "red"))
    return text

def strip(text):
    return text.rstrip("\n ")


def wrap(text, line_length, padding):
    """
    Wraps text at cutoff line_length and shifts it right by an
    padding amount
    """

    line_length = line_length - padding
    join_str = "\n" + " " * padding
    word_list = [word.strip(" \n") for word in text.split(" ")]
    line = ""
    line_list = []
    while len(word_list):
        word = word_list.pop(0)
        if not line:
            if len(word) < line_length:
                line = word
            else:
                line_list.append(word)
        else:
            if len(line) + len(word) < line_length:
                line = "%s %s" % (line, word)
            else:
                line_list.append(line)
                line = word
    if line:
        line_list.append(line)
    output = "\n".join(line_list).replace("\n", join_str)
    return " " * padding + output
