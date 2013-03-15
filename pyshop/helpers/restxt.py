from docutils import core
from docutils.utils import SystemMessage
from jinja2 import Markup


def parse_rest(rest):
    try:
        html = core.publish_string(
            source=rest,
            writer_name='html',
            settings_overrides={'output_encoding': 'unicode'})
        return Markup(html[html.find('<body>') + 6:html.find('</body>')].strip())
    except SystemMessage:
        return Markup('<pre>' + rest + '</pre>')
