from django import template
from toonkor_collector2.toonkor_api import toonkor_api


register = template.Library()

@register.simple_tag(takes_context=True)
def theme(context):
    request = context['request']
    theme = request.COOKIES.get('theme', 'light')
    return theme


@register.simple_tag(takes_context=True)
def toonkor_url(context):
    request = context['request']
    url = request.COOKIES.get('toonkor_url', toonkor_api.base_url)
    return url