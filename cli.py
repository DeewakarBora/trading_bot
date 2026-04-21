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
            "  Interactive: python cli.py\n"
        ),
    )
    parser.add_argument("--symbol", required=False, metavar="SYMBOL",
                        help="Trading pair symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", required=False, choices=["BUY", "SELL"],
                        metavar="SIDE", help="Order side: BUY or SELL")
    parser.add_argument("--type", required=False, dest="order_type",
                        choices=["MARKET", "LIMIT"], metavar="TYPE",
                        help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", required=False, metavar="QTY",
                        help="Order quantity (e.g. 0.001)")
    parser.add_argument("--price", required=False, default=None,
                        metavar="PRICE", help="Limit price (required for LIMIT orders)")
    return parser


def _load_credentials() -> tuple[str, str]:
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        logger.error("Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        _print_failure("Missing API credentials. Please set them in your .env file.")
        sys.exit(1)
    return api_key, api_secret


def _print_success(message: str) -> None:
    print(f"\n  ✅  {message}\n")


def _print_failure(message: str) -> None:
    print(f"\n  ❌  {message}\n")


def _print_banner() -> None:
    print("""
  ╔══════════════════════════════════════════╗
  ║     Binance Futures Testnet Trading Bot  ║
  ║         Interactive Mode                 ║
  ╚══════════════════════════════════════════╝
    """)


def _prompt(label: str, options: list = None, default: str = None) -> str:
    """Prompt user for input with optional choices and default value."""
    if options:
        opts = "/".join(options)
        prompt_str = f"  ➤  {label} [{opts}]"
    else:
        prompt_str = f"  ➤  {label}"
    if default:
        prompt_str += f" (default: {default})"
    prompt_str += ": "

    while True:
        value = input(prompt_str).strip()
        if not value and default:
            return default
        if options and value.upper() not in [o.upper() for o in options]:
            print(f"      ⚠️  Invalid choice. Please enter one of: {', '.join(options)}")
            continue
        if not value:
            print(f"      ⚠️  This field is required.")
            continue
        return value.upper() if options else value


def interactive_mode() -> dict:
    """Guide user through order placement interactively."""
    _print_banner()
    print("  No arguments detected — launching interactive mode.\n")
    print("  Press Ctrl+C at any time to exit.\n")

    try:
        symbol     = _prompt("Symbol", default="BTCUSDT")
        symbol     = symbol.upper()

        side       = _prompt("Side", options=["BUY", "SELL"])
        order_type = _prompt("Order type", options=["MARKET", "LIMIT"])
        quantity   = _prompt("Quantity (e.g. 0.001)")

        price = None
        if order_type == "LIMIT":
            price = _prompt("Limit price (e.g. 30000)")

        return {
            "symbol":     symbol,
            "side":       side,
            "order_type": order_type,
            "quantity":   quantity,
            "price":      price,
        }
    except KeyboardInterrupt:
        print("\n\n  Exiting. Goodbye!\n")
        sys.exit(0)


def _execute_order(symbol, side, order_type, quantity, price):
    """Validate, build client, place order and print results."""

    # Validate
    try:
        validated = validate_all(
            symbol=symbol, side=side, order_type=order_type,
            quantity=quantity, price=price,
        )
    except ValidationError as exc:
        _print_failure(f"Validation error: {exc}")
        logger.error("Validation failed: %s", exc)
        sys.exit(1)

    # Print order summary
    print(format_order_summary(validated))

    # Confirm in interactive mode
    try:
        confirm = input("  ➤  Confirm and place order? [yes/no]: ").strip().lower()
        if confirm not in ("yes", "y"):
            print("\n  Order cancelled.\n")
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Order cancelled.\n")
        sys.exit(0)

    # Load credentials
    api_key, api_secret = _load_credentials()

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        _print_failure(str(exc))
        sys.exit(1)

    # Place order
    try:
        response = place_order(
            client=client, symbol=validated["symbol"],
            side=validated["side"], order_type=validated["order_type"],
            quantity=validated["quantity"], price=validated["price"],
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

    print(format_order_response(response))
    _print_success("Order placed successfully!")
    logger.info("Trading bot finished successfully")
    logger.info("=" * 60)


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Trading bot started")

    # If no arguments provided — launch interactive mode
    if not any([args.symbol, args.side, args.order_type, args.quantity]):
        inputs = interactive_mode()
        _execute_order(**inputs)
    else:
        # CLI mode — validate all required args are present
        missing = []
        if not args.symbol:     missing.append("--symbol")
        if not args.side:       missing.append("--side")
        if not args.order_type: missing.append("--type")
        if not args.quantity:   missing.append("--quantity")
        if missing:
            _print_failure(f"Missing required arguments: {', '.join(missing)}")
            parser.print_help()
            sys.exit(1)

        _execute_order(
            symbol=args.symbol, side=args.side,
            order_type=args.order_type, quantity=args.quantity,
            price=args.price,
        )


if __name__ == "__main__":
    main()