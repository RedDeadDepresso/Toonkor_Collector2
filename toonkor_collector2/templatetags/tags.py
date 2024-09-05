from django import template
from toonkor_collector2.toonkor_api import toonkor_api

register = template.Library()


@register.simple_tag(takes_context=True)
def theme(context):
    request = context["request"]
    return request.COOKIES.get("theme", "light")


def get_display_english(context):
    request = context["request"]
    return request.COOKIES.get("display_english", "true") == "true"


def get_en_dict(manhwa, key):
    en_key = f"en_{key}"
    return manhwa.get(en_key, manhwa[key])


def get_en_db(manhwa, key):
    en_key = f"en_{key}"
    return getattr(manhwa, en_key, getattr(manhwa, key, ""))


@register.simple_tag(takes_context=True)
def display_title(context, manhwa):
    is_dict = isinstance(manhwa, dict)
    if get_display_english(context):
        return get_en_dict(manhwa, "title") if is_dict else get_en_db(manhwa, "title")
    else:
        return manhwa["title"] if is_dict else manhwa.title


@register.simple_tag(takes_context=True)
def display_description(context, manhwa):
    is_dict = isinstance(manhwa, dict)
    if get_display_english(context):
        return (
            get_en_dict(manhwa, "description")
            if is_dict
            else get_en_db(manhwa, "description")
        )
    else:
        return manhwa["description"] if is_dict else manhwa.description


@register.simple_tag(takes_context=True)
def toonkor_url(context):
    request = context["request"]
    return request.COOKIES.get("toonkor_url", toonkor_api.base_url)
