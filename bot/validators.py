import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.validators")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}

SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,10}USDT$")


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(value):
        raise ValidationError(
            f"Invalid symbol '{value}'. Expected format: BTCUSDT, ETHUSDT, etc."
        )
    logger.debug("Symbol validated: %s", value)
    return value


def validate_side(side: str) -> str:
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{value}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    logger.debug("Side validated: %s", value)
    return value


def validate_order_type(order_type: str) -> str:
    value = order_type.strip().upper()
    if value not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{value}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    logger.debug("Order type validated: %s", value)
    return value


def validate_quantity(quantity: str) -> Decimal:
    try:
        value = Decimal(str(quantity))
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if value <= 0:
        raise ValidationError(f"Quantity must be greater than zero, got {value}.")
    logger.debug("Quantity validated: %s", value)
    return value


def validate_price(price: Optional[str], order_type: str) -> Optional[Decimal]:
    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            value = Decimal(str(price))
        except InvalidOperation:
            raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
        if value <= 0:
            raise ValidationError(f"Price must be greater than zero, got {value}.")
        logger.debug("Price validated: %s", value)
        return value

    if price is not None:
        logger.debug("Price '%s' ignored for MARKET order.", price)
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
) -> dict:
    """
    Run all validations and return a clean, typed parameter dict.
    Raises ValidationError on first failure.
    """
    validated_type = validate_order_type(order_type)
    return {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": validated_type,
        "quantity":   validate_quantity(quantity),
        "price":      validate_price(price, validated_type),
    }