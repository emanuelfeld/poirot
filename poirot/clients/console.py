import sys
import subprocess

from abstract import AbstractClient
from jinja2 import Environment, PackageLoader
from style import fail, ok, highlight, style


class ConsoleClient(AbstractClient):

    def __init__(self):
        pass

    def render(self, terms, data, info):
        env = Environment(loader=PackageLoader('poirot', 'templates'))
        env.filters['ok'] = ok
        env.filters['fail'] = fail
        env.filters['style'] = style
        env.filters['highlight'] = highlight
        template = env.get_template('console.html')

        data_to_render = template.render(data=data, info=info)

        try:
            pager = subprocess.Popen(['less', '-F', '-R', '-S', '-X', '-K'],
                        stdin=subprocess.PIPE, stdout=sys.stdout)
            lines = data_to_render.split('\n')
            for line in lines:
                pager.stdin.write(line.encode('utf-8') + '\n')
            pager.stdin.close()
            pager.wait()
        except KeyboardInterrupt:
            pass
