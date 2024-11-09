import base64
from django import template

register = template.Library()

@register.filter
def b64encode(value):
    if isinstance(value, bytes):
        # Handle if value is already bytes (e.g., BytesIO content)
        return base64.b64encode(value).decode()
    elif isinstance(value, str):
        # Encode string values
        return base64.b64encode(value.encode()).decode()
    else:
        raise ValueError("Unsupported value type for b64encode filter.")

