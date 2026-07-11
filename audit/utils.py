from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


def instance_to_dict(instance):
    """Convierte una instancia de modelo a un dict JSON-serializable."""
    result = {}
    for field in instance._meta.concrete_fields:
        value = getattr(instance, field.attname)
        if value is None:
            result[field.attname] = None
        elif isinstance(value, (int, float, str, bool)):
            result[field.attname] = value
        elif isinstance(value, Decimal):
            result[field.attname] = float(value)
        elif isinstance(value, (date, datetime)):
            result[field.attname] = value.isoformat()
        elif isinstance(value, UUID):
            result[field.attname] = str(value)
        else:
            try:
                result[field.attname] = str(value)
            except Exception:
                result[field.attname] = None
    return result
