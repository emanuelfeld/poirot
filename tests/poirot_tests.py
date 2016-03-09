# -*- coding: utf-8 -*-
import os

from poirot.poirot import main as poirot_main
from poirot.style import *
from nose.tools import *
from poirot.helpers import *
from poirot.parser import parse_arguments

def setUp():
    global case, args, test_repo, test_dir
    current_dir = os.path.dirname(os.path.realpath(__file__))
    test_repo = 'https://github.com/DCgov/poirot-test-repo.git'
    test_dir = '{}/fixtures'.format(current_dir)
    args = [
                '--url={url}'.format(url=test_repo),
                '--revlist=all',
                '--dir={dir}'.format(dir=test_dir),
                '--patterns=poirot/patterns/default.txt, https://raw.githubusercontent.com/DCgov/poirot-patterns/master/default.txt',
                '--term=frabjous'
            ]
    case = parse_arguments(args)


def tearDown():
    pass


def test_execute_cmd():
    (out, err) = execute_cmd(['echo', '人'])
    eq_(out.find('人') == 0, True)
    eq_(err, '')


def test_ask():
    response = ask(question='Answer y', options=['y', 'n'], response='y')
    eq_(response, 'y')


def test_merge_dicts():
    merged = merge_dicts({"a": True, "b": False}, {"a": False})
    eq_(merged, {"a": False, "b": False})


def test_case_parser():
    eq_(len(case), 11)
    eq_(len(case['patterns']), 18)
    eq_(case['revlist'], ['--all'])
    eq_(case['git_url'], 'https://github.com/DCgov/poirot-test-repo.git')


def test_find_matches():
    results = poirot_main(args=args, render_results=False)
    print(results)
    frabjous = results['frabjous']
    eq_(frabjous['f0a6ebc']['author_email'], 'emanuelfeld@users.noreply.github.com')
    eq_(len(frabjous), 4)
    eq_(len(frabjous['f0a6ebc']['files']), 2)
    eq_(frabjous['f0a6ebc']['files'][0]['matches'][0]['line'], 12)
    eq_(frabjous['f0a6ebc']['files'][1]['matches'][0]['line'], 2)
    eq_(frabjous['label'], '')

    # password = poirot.findings['pass(word?)[[:blank:]]*[=:][[:blank:]]*.+']
    # eq_(len(password), 3)
    # eq_(password['label'], 'Usernames and Passwords')
    # ok_('log' in password['2f04563'].keys())


# def test_parse_post_diff():
#     results = [(sha, metadata) for sha, metadata in parse_post(target='diff', pattern='frabjous', git_dir='{}/.git'.format(test_dir), revlist='cd956e8^!')]
#     eq_(len(results), 1)
#     eq_(results[0][0], 'cd956e8')
#     eq_(len(results[0][1]['files']), 1)


# def test_parse_post_message():
#     results = [(sha, metadata) for sha, metadata in parse_post(target='message', pattern='fake@fake.biz', git_dir='{}/.git'.format(test_dir), revlist='--all')]
#     eq_(len(results), 1)
#     eq_(results[0][0], '49a1c77')
#     eq_(results[0][1]['log'].find('fake@fake.biz') == 0, True)


# def test_chunk_text():
#     output = chunk_text(text='a b c d e f g', cutoff=3, offset=0).split('\n')
#     eq_(output[0], 'a b')


# def test_style_color():
#     for code in style_codes:
#         ok_(style("testing", code))
