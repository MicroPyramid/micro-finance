from django import template
import decimal
register = template.Library()


@register.filter
def demand_collections_difference(demand, collection):
    if demand is None:
        demand = 0
    if collection is None:
        collection = 0
    diff = decimal.Decimal(decimal.Decimal(demand) - decimal.Decimal(collection))
    return diff
