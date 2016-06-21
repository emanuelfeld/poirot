# -*- coding: utf-8 -*-

import os
from copy import copy

from poirot.poirot import *
from poirot.filters import *
from nose.tools import *
from poirot.utils import *
from poirot.parser import parse_arguments


def setUp():
    global info, args, output_args, test_repo, test_dir
    current_dir = os.path.dirname(os.path.realpath(__file__))
    test_repo = "https://github.com/emanuelfeld/poirot-test-repo.git"
    test_dir = "{}/fixtures".format(current_dir)
    execute_cmd(["mkdir", test_dir])
    args = [
        "--url={url}".format(url=test_repo),
        "--revlist=all",
        "--dir={dir}".format(dir=test_dir),
        "--patterns=poirot/patterns/default.txt, https://raw.githubusercontent.com/emanuelfeld/poirot-patterns/master/default.txt",
        "--term=frabjous",
        "--output={dir}/test_results.json".format(dir=test_dir)
    ]
    info = parse_arguments(args)


def tearDown():
    execute_cmd(["rm", "-rf", test_dir])


def test_execute_cmd():
    (out, err) = execute_cmd(["echo", "人"])
    eq_(out.find("人") == 0, True)
    eq_(err, "")


def test_ask():
    response = ask(question="Answer y", options=["y", "n"], response="y")
    eq_(response, "y")


def test_merge_dicts():
    merged = merge_dicts({"a": True, "b": False}, {"a": False})
    eq_(merged, {"a": False, "b": False})


def test_info_parser():
    eq_(len(info), 12)
    eq_(len(info["patterns"]), 18)
    eq_(info["revlist"], ["--all"])
    eq_(info["git_url"], "https://github.com/emanuelfeld/poirot-test-repo.git")


def test_find_matches():
    results = main(args=args, render_results=False)
    frabjous = results["frabjous"]
    eq_(frabjous["f0a6ebc"]["author_email"], "emanuelfeld@users.noreply.github.com")
    eq_(len(frabjous), 3)
    eq_(len(frabjous["f0a6ebc"]["files"]), 2)
    eq_(frabjous["f0a6ebc"]["files"][0]["matches"][0]["line"], 12)
    eq_(frabjous["f0a6ebc"]["files"][1]["matches"][0]["line"], 2)
    eq_(info["patterns"]["frabjous"], None)

    password = results["pass(word?)[[:blank:]]*[=:][[:blank:]]*.+"]
    eq_(len(password), 2)
    eq_(info["patterns"]["pass(word?)[[:blank:]]*[=:][[:blank:]]*.+"], "Usernames and Passwords")
    ok_("log" in password["2f04563"].keys())

    # test JSON output
    with open("{}/test_results.json".format(test_dir)) as infile:
        results = json.load(infile)
    eq_("cd956e8" in results["frabjous"], True)


def test_parse_post_diff():
    results = [(sha, metadata) for sha, metadata in search_committed(target="diff", pattern="frabjous", revlist="cd956e8^!", info=info)]
    eq_(len(results), 1)
    eq_(results[0][0], "cd956e8")
    eq_(len(results[0][1]["files"]), 1)


def test_parse_post_message():
    results = [(sha, metadata) for sha, metadata in search_committed(target="message", pattern="fake@fake.biz", revlist="--all", info=info)]
    eq_(len(results), 1)
    eq_(results[0][0], "49a1c77")
    eq_(results[0][1]["log"].find("fake@fake.biz") == 0, True)


def test_chunk_text():
    output = wrap(text="a b c d e f g", line_length=3, padding=0).split("\n")
    eq_(output[0], "a b")


def test_style_color():
    for code in STYLE_CODES:
        ok_(style("testing", code))
