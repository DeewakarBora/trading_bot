import os
import sys

import argparse
from dotenv import load_dotenv

from bot.client import BinanceClientError, BinanceFuturesClient, NetworkError
from bot.logging_config import setup_logger
from bot.orders import format_order_response, format_order_summary, place_order
from bot.validators import ValidationError, validate_all

load_dotenv()
logger = setup_logger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — CLI Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Market BUY:  python cli.py --symbol BTCUSDT --side BUY "
            "--type MARKET --quantity 0.001\n"
            "  Limit SELL:  python cli.py --symbol ETHUSDT --side SELL "
            "--type LIMIT --quantity 0.01 --price 2000\n"
        ),
    )
    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol (e.g. BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT"],
        metavar="TYPE",
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        metavar="QTY",
        help="Order quantity (e.g. 0.001)",
    )
    parser.add_argument(
        "--price",
        required=False,
        default=None,
        metavar="PRICE",
        help="Limit price — required for LIMIT orders (e.g. 30000)",
    )
    return parser


def _load_credentials() -> tuple[str, str]:
    """Load API credentials from environment; exit cleanly if missing."""
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        logger.error(
            "Missing API credentials. "
            "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file."
        )
        sys.exit(1)

    return api_key, api_secret


def _print_success(message: str) -> None:
    print(f"\n  ✅  {message}\n")


def _print_failure(message: str) -> None:
    print(f"\n  ❌  {message}\n")


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Trading bot started")

    # ── Validate inputs ──────────────────────────────────────────
    try:
        validated = validate_all(
            symbol     = args.symbol,
            side       = args.side,
            order_type = args.order_type,
            quantity   = args.quantity,
            price      = args.price,
        )
    except ValidationError as exc:
        _print_failure(f"Validation error: {exc}")
        logger.error("Validation failed: %s", exc)
        sys.exit(1)

    # ── Print order summary ───────────────────────────────────────
    print(format_order_summary(validated))

    # ── Load credentials & build client ──────────────────────────
    api_key, api_secret = _load_credentials()

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        _print_failure(str(exc))
        logger.error("Client init failed: %s", exc)
        sys.exit(1)

    # ── Place order ───────────────────────────────────────────────
    try:
        response = place_order(
            client     = client,
            symbol     = validated["symbol"],
            side       = validated["side"],
            order_type = validated["order_type"],
            quantity   = validated["quantity"],
            price      = validated["price"],
        )
    except ValidationError as exc:
        _print_failure(f"Validation error: {exc}")
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except BinanceClientError as exc:
        _print_failure(f"Binance API error {exc.code}: {exc.message}")
        logger.error("Binance API error: %s", exc)
        sys.exit(1)
    except NetworkError as exc:
        _print_failure(f"Network error: {exc}")
        logger.error("Network error: %s", exc)
        sys.exit(1)

    # ── Print response ────────────────────────────────────────────
    print(format_order_response(response))
    _print_success("Order placed successfully!")
    logger.info("Trading bot finished successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()