from django import template

register = template.Library()

@register.filter(name='currency_naira')
def currency_naira(value):
    """
    Custom Django template filter to display numbers with the Naira (₦) symbol
    and add commas for thousands separators.
    """
    try:
        # Format value as a number with commas and Naira symbol
        return f"₦{value:,.2f}"
    except (ValueError, TypeError):
        # Handle the case where value is None or not a number
        return "₦0.00"
