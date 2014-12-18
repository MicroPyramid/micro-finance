from django import template
register = template.Library()
import decimal

@register.filter
def demand_collections_difference(demand, collection):
    if decimal.Decimal(demand) > decimal.Decimal(collection) :
        diff = decimal.Decimal(decimal.Decimal(demand) - decimal.Decimal(collection))
        return diff
    else:
        return 0

