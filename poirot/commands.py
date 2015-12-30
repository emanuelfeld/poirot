#! /usr/bin/env python
# -*- codes: utf-8 -*-

import sys
from .poirot import Poirot, Case
from .clients import ConsoleClient, ConsoleThinClient


def littlegreycells(args=sys.argv):
    args.pop(0)
    client = ConsoleThinClient()
    case = Case(args)
    poirot = Poirot(client, case)
    poirot.prepare()
    poirot.investigate()
    poirot.report()


def biggreycells(args=sys.argv):
    args.pop(0)
    client = ConsoleClient()
    case = Case(args)
    poirot = Poirot(client, case)
    poirot.prepare()
    poirot.investigate()
    poirot.report()
