from decimal import Decimal
from typing import Any, Dict, Optional

from bot.client import BinanceClientError, BinanceFuturesClient, NetworkError
from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.orders")

ORDER_ENDPOINT = "/fapi/v1/order"


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
) -> Dict[str, Any]:
    """Build the raw parameter dict for the order endpoint."""
    params: Dict[str, Any] = {
        "symbol":   symbol,
        "side":     side,
        "type":     order_type,
        "quantity": str(quantity),
    }
    if order_type == "LIMIT":
        params["price"]       = str(price)
        params["timeInForce"] = "GTC"   # Good Till Cancelled

    return params


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
) -> Dict[str, Any]:
    """
    Place a MARKET or LIMIT order on Binance Futures Testnet.

    Returns the raw API response dict on success.
    Propagates BinanceClientError or NetworkError on failure.
    """
    params = _build_order_params(symbol, side, order_type, quantity, price)

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s%s",
        side,
        order_type,
        symbol,
        quantity,
        f" price={price}" if price else "",
    )
    logger.debug("Order request params: %s", params)

    try:
        response = client.post(ORDER_ENDPOINT, params=params)
    except BinanceClientError as exc:
        logger.error("Order rejected by Binance | code=%s msg=%s", exc.code, exc.message)
        raise
    except NetworkError as exc:
        logger.error("Network error while placing order: %s", exc)
        raise

    logger.info(
        "Order accepted | orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice", "N/A"),
    )
    logger.debug("Full order response: %s", response)

    return response


def format_order_summary(params: Dict[str, Any]) -> str:
    """Return a human-readable summary of the order request."""
    lines = [
        "",
        "  ┌─────────────────────────────────┐",
        "  │         ORDER REQUEST            │",
        "  ├─────────────────────────────────┤",
        f"  │  Symbol    : {params.get('symbol', ''):<20}│",
        f"  │  Side      : {params.get('side', ''):<20}│",
        f"  │  Type      : {params.get('order_type', ''):<20}│",
        f"  │  Quantity  : {str(params.get('quantity', '')):<20}│",
        f"  │  Price     : {str(params.get('price') or 'MARKET'):<20}│",
        "  └─────────────────────────────────┘",
    ]
    return "\n".join(lines)


def format_order_response(response: Dict[str, Any]) -> str:
    """Return a human-readable summary of the order response."""
    avg_price = response.get("avgPrice") or response.get("price", "N/A")
    lines = [
        "",
        "  ┌─────────────────────────────────┐",
        "  │         ORDER RESPONSE           │",
        "  ├─────────────────────────────────┤",
        f"  │  Order ID  : {str(response.get('orderId', '')):<20}│",
        f"  │  Status    : {response.get('status', ''):<20}│",
        f"  │  Exec Qty  : {str(response.get('executedQty', '')):<20}│",
        f"  │  Avg Price : {str(avg_price):<20}│",
        f"  │  Symbol    : {response.get('symbol', ''):<20}│",
        f"  │  Side      : {response.get('side', ''):<20}│",
        "  └─────────────────────────────────┘",
    ]
    return "\n".join(lines)