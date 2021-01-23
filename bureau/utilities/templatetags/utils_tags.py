from django import template

register = template.Library()

@register.filter
def partial_date(value):
    return value.format('%Y', '%b. %Y', '%b. %d, %Y')
