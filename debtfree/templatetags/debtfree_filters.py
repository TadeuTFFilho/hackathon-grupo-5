from django import template

register = template.Library()


@register.filter(name='brl')
def brl(value):
    """Format a number as Brazilian Real: R$ 1.240,90"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value) if value is not None else ''

    formatted = f"{v:,.2f}"                              # "1,240.90"
    formatted = formatted.replace('.', 'X').replace(',', '.').replace('X', ',')
    return f"R$ {formatted}"


@register.filter(name='brl_abs')
def brl_abs(value):
    """Format absolute value of a number as BRL."""
    try:
        v = abs(float(value))
    except (TypeError, ValueError):
        return str(value) if value is not None else ''

    formatted = f"{v:,.2f}"
    formatted = formatted.replace('.', 'X').replace(',', '.').replace('X', ',')
    return f"R$ {formatted}"
