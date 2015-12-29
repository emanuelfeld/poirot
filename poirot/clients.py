import sys
import subprocess

from abc import ABCMeta, abstractmethod
from jinja2 import Environment, PackageLoader
from .style import fail, ok, highlight, style, chunk_text, strip


class AbstractClient:
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, data):
        """
        Each instance of an AbstractClient must implement a render method, 
        which is called by Poirot
        """
        raise Exception


class ConsoleClient(AbstractClient):

    def __init__(self):
        pass

    def render(self, data, info):
        env = Environment(loader=PackageLoader('poirot', 'templates'))
        env.filters['ok'] = ok
        env.filters['fail'] = fail
        env.filters['style'] = style
        env.filters['chunk_text'] = chunk_text
        env.filters['strip'] = strip
        env.filters['highlight'] = highlight

        template = env.get_template('console.html')

        data_to_render = template.render(data=data, info=info)

        try:
            cmd = ['less', '-F', '-R', '-S', '-X', '-K']
            pager = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=sys.stdout)
            lines = data_to_render.split('\n')
            for line in lines:
                pager.stdin.write(line.encode('utf-8') + b'\n')
            pager.stdin.close()
            pager.wait()
        except KeyboardInterrupt:
            pass


class ConsoleThinClient(AbstractClient):
    """
    Implements a minimal template for use in automated environemnts,
    e.g. continuous integration and git commit hooks
    """

    def __init__(self):
        pass

    def render(self, data, info):
        env = Environment(loader=PackageLoader('poirot', 'templates'))
        env.filters['chunk_text'] = chunk_text
        env.filters['strip'] = strip
        template = env.get_template('console_thin.html')

        data_to_render = template.render(data=data, info=info)

        print(data_to_render)
