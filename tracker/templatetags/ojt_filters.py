from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage_color(pct):
    """Return Bootstrap color class based on completion %."""
    pct = float(pct)
    if pct >= 100:
        return 'success'
    elif pct >= 75:
        return 'info'
    elif pct >= 50:
        return 'primary'
    elif pct >= 25:
        return 'warning'
    return 'danger'

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
