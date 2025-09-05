from django import template

register = template.Library()


@register.filter
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return ','.join(str(int(value[i:i + lv // 3], 16)) for i in range(0, lv, lv // 3))


def darken_hex(hex_color, percent=20):
    """Darken a hex color by a percentage."""
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    rgb = [int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3)]
    darker = [max(0, int(c * (1 - percent / 100))) for c in rgb]
    return '#{:02X}{:02X}{:02X}'.format(*darker)


@register.filter
def darken(value, percent=20):
    return darken_hex(value, percent)
