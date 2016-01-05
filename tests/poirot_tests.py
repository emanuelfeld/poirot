from poirot.poirot import Case, Poirot
from poirot.style import *
from nose.tools import *
from poirot.helpers import *


def setUp():
    global case, poirot
    args = ['-u', 'https://github.com/DCgov/poirot-test-repo.git', '--revlist=all', '--dir=tests/fixtures', '--patterns=poirot/patterns/default.txt', '--term', 'frabjous']
    case = Case(args)
    case_parser_test()
    poirot = Poirot(case)
    poirot.investigate()
    find_matches_test()
    style_color_test()


def tearDown():
    pass


def case_parser_test():
    eq_(len(case.__dict__), 11)
    eq_(len(case.patterns), 16)
    eq_(case.revlist, ['--all'])
    eq_(case.git_url, 'https://github.com/DCgov/poirot-test-repo.git')


def find_matches_test():
    frabjous = poirot.findings['frabjous']
    eq_(frabjous['f0a6ebc']['author_email'], 'emanuelfeld@users.noreply.github.com')
    eq_(len(frabjous), 3)
    eq_(len(frabjous['f0a6ebc']['files']), 2)
    eq_(frabjous['f0a6ebc']['files'][0]['matches'][0]['line'], 12)
    eq_(frabjous['f0a6ebc']['files'][1]['matches'][0]['line'], 2)

    password = poirot.findings['pass(word?)[[:blank:]]*[=:][[:blank:]]*.+']
    eq_(len(password), 2)
    ok_('log' in password['2f04563'].keys())


def style_color_test():
    for code in style_codes:
        ok_(style("testing", code))
