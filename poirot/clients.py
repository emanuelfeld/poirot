# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import subprocess
from jinja2 import Environment, PackageLoader

from .filters import fail, ok, highlight, style, wrap, strip
from .utils import merge_dicts


def render(results, case):
    env = Environment(loader=PackageLoader("poirot", "templates"))
    filters = {
        "ok": ok,
        "fail": fail,
        "style": style,
        "wrap": wrap,
        "strip": strip,
        "highlight": highlight
    }

    env.filters = merge_dicts(env.filters, filters)

    if not case["verbose"]:
        template = env.get_template("console_thin.html")
        data_to_render = template.render(data=results, info=case)
        print(data_to_render)
    else:
        template = env.get_template("console.html")
        data_to_render = template.render(data=results, info=case)
        try:
            cmd = ["less", "-F", "-R", "-S", "-X", "-K"]
            pager = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=sys.stdout)
            lines = data_to_render.split("\n")
            for line in lines:
                pager.stdin.write(line.encode("utf-8") + b"\n")
            pager.stdin.close()
            pager.wait()
        except KeyboardInterrupt:
            pass
        except BrokenPipeError:
            pass
