from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

def data_hoje():
    return datetime.today()

def converter_data(data: str):
    return datetime.strptime(data, "%Y-%m-%d")

def to_monetary_decimal(valor: str | Decimal) -> Decimal:
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)