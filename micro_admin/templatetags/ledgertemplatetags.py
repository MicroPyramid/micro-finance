from django import template
import decimal
register = template.Library()


@register.filter
def demand_collections_difference(demand, collection):
    if demand and collection:
        if decimal.Decimal(demand) > decimal.Decimal(collection):
            diff = decimal.Decimal(decimal.Decimal(demand) - decimal.Decimal(collection))
            return diff
    else:
        return 0
