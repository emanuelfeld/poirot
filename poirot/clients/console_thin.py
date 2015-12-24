from poirot.clients.abstract import AbstractClient
from poirot.clients.style import chunk_text, strip
from jinja2 import Environment, PackageLoader


class ConsoleThinClient(AbstractClient):
    """
    Command-line client for Poirot that emits the bare essentials.
    Useful for automated environments, such as continuous integration
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
