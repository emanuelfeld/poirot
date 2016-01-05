#! /usr/bin/env python
# -*- codes: utf-8 -*-

import sys
from .poirot import Poirot, Case


def poirot(args=sys.argv):
    args.pop(0)
    case = Case(args)
    poirot = Poirot(case)
    poirot.prepare()
    poirot.investigate()
    poirot.report()
