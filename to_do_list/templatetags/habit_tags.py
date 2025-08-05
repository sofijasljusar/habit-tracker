from django import template

register = template.Library()


@register.filter
def get_date(records, date_string):
    return records.filter(date=date_string).first()
