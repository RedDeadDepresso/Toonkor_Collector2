from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def theme(context):
    request = context['request']
    theme = request.COOKIES.get('theme', 'light')
    return theme