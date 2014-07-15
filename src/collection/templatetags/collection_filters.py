from django import template
import os, urllib, utils.enum

register = template.Library()

@register.tag
def make_list(parser, token):
    bits = list(token.split_contents())
    if len(bits) >= 4 and bits[-2] == "as":
        varname = bits[-1]
        items = bits[1:-2]
        return MakeListNode(items, varname)
    else:
        raise template.TemplateSyntaxError("%r expected format is 'item [item ...] as varname'" % bits[0])

class MakeListNode(template.Node):
    def __init__(self, items, varname):
        self.items = map(template.Variable, items)
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = [ i.resolve(context) for i in self.items ]
        return ""


@register.filter
def dict_get(d, key):
    return d[key]

@register.filter
def urldecode(value):
    return urllib.unquote(value).decode('iso-8859-2')

@register.filter
def url_join(value):
    return os.path.join(*value)

@register.filter
def get_readable_permission(value):
    for (k,v) in utils.enum.Permission.CHOICES:
        if k==value:
            return v
        
@register.filter
def is_anonymous(value):
    return value.is_anonymous()