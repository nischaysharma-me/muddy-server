"""Currency Converter Marketplace Tool Handler."""

from typing import Any, Dict
from app.tools.plugins.base import BaseToolPlugin


class CurrencyConverterTool(BaseToolPlugin):
    """Converts amounts between global fiat currencies."""

    _RATES = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 154.5,
        "INR": 86.5,
        "CAD": 1.38,
        "AUD": 1.52,
    }

    async def execute(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        from_code = from_currency.upper().strip()
        to_code = to_currency.upper().strip()

        from_rate = self._RATES.get(from_code, 1.0)
        to_rate = self._RATES.get(to_code, 1.0)

        usd_value = amount / from_rate
        converted = usd_value * to_rate

        return {
            "amount": amount,
            "from_currency": from_code,
            "to_currency": to_code,
            "converted_amount": round(converted, 2),
            "exchange_rate": round(to_rate / from_rate, 4),
        }
