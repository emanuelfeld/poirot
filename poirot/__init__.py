#! /usr/bin/env python
# -*- codes: utf-8 -*-
import sys
from poirot.poirot import Poirot, Case
from poirot.clients import ConsoleClient

__version__ = '0.0.1'

if __name__ == '__main__':
    sys.argv.pop(0)
    client = ConsoleClient()
    case = Case(sys.argv)
    poirot = Poirot(client, case)
    poirot.prepare()
    poirot.investigate()
    poirot.report()
