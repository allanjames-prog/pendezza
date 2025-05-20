# salon/templatetags/review_filters.py
from django import template

register = template.Library()

@register.filter
def chunks(lst, chunk_size):
    """Split a list into chunks of specified size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]