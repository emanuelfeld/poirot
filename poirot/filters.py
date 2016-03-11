# -*- coding: utf-8 -*-

import regex

prefix = "\033["
reset = prefix + "0m"

style_codes = {
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

for code in style_codes:
    style_codes[code] = prefix + style_codes[code]

symbol_codes = {
  'ok': u"\u2713",
  'fail': u"\u2716",
}


def style(text, _code):
    """Takes a string and styles its print output"""

    try:
        return "%s%s%s" % (style_codes[_code], text, reset)
    except:
        return "%s" % (text)


def ok(text):
    """Takes a string and prepends a green check to it"""

    return "%s %s" % (style(symbol_codes['ok'], 'green'), text)


def fail(text=''):
    """Takes a string and prepends a red x mark to it"""

    return "%s %s" % (style(symbol_codes['fail'], 'red'), text)


def highlight(text, pattern):
    """Takes a string and highlights substrings matching a pattern"""

    pattern_re = regex.compile(pattern, regex.I)
    match = pattern_re.search(text)
    if match:
        text = text.replace(match.group(0), style(match.group(0), 'red'))
    return text


def strip(text):
    return text.rstrip('\n ')


def wrap(text, cutoff, offset):
    """
    Wraps text at cutoff length and shifts it right by an offset amount
    """

    cutoff = cutoff - offset
    join_str = '\n' + " "*offset
    split = text.split(' ')
    chunk = ''
    chunked = []
    while len(split):
        word = split.pop(0)
        word = word.strip(' \n')
        if not chunk and len(word) < cutoff:
            chunk = word
        elif not chunk and len(word) > cutoff:
            chunked.append(word)
        elif len(chunk) + len(word) < cutoff:
            chunk = "%s %s" % (chunk, word)
        else:
            chunked.append(chunk)
            chunk = word
    if chunk:
        chunked.append(chunk)
    output = '\n'.join(chunked).replace('\n', join_str)
    return " "*offset + output
