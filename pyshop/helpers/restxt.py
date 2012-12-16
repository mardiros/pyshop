from docutils import core
from jinja2 import Markup


def parse_rest(rest):
    html = core.publish_string(
               source=rest,
               writer_name='html',
               settings_overrides={'output_encoding': 'unicode'})
    return Markup(html[html.find('<body>')+6:html.find('</body>')].strip())
