# Trading Bot — Binance Futures Testnet

A clean, production-style Python CLI trading bot that places **Market** and **Limit** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance REST API client (signing, requests, errors)
│   ├── orders.py            # Order placement logic + output formatters
│   ├── validators.py        # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py    # Structured logging (file + console)
├── logs/                    # Auto-created log files
├── cli.py                   # CLI entry point (argparse)
├── .env                     # API credentials (never committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/trading_bot.git
cd trading_bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API credentials

Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

Get your credentials from [Binance Futures Testnet](https://testnet.binancefuture.com).

---

## How to Run

### Place a Market BUY order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Market SELL order

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a Limit BUY order

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 30000
```

### Place a Limit SELL order

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 2000
```

### View all options

```bash
python cli.py --help
```

---

## Example Output

```
  ┌─────────────────────────────────┐
  │         ORDER REQUEST            │
  ├─────────────────────────────────┤
  │  Symbol    : BTCUSDT             │
  │  Side      : BUY                 │
  │  Type      : MARKET              │
  │  Quantity  : 0.001               │
  │  Price     : MARKET              │
  └─────────────────────────────────┘

  ┌─────────────────────────────────┐
  │         ORDER RESPONSE           │
  ├─────────────────────────────────┤
  │  Order ID  : 123456789           │
  │  Status    : FILLED              │
  │  Exec Qty  : 0.001               │
  │  Avg Price : 30000.00            │
  │  Symbol    : BTCUSDT             │
  │  Side      : BUY                 │
  └─────────────────────────────────┘

  ✅  Order placed successfully!
```

---

## Logging

All activity is logged to `logs/trading_bot_YYYYMMDD.log`:

- **DEBUG** — full request/response payloads
- **INFO** — order lifecycle events
- **ERROR** — validation failures, API errors, network issues

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing/invalid symbol | `ValidationError` with clear message |
| Missing price on LIMIT order | `ValidationError` with clear message |
| Invalid quantity or price | `ValidationError` with clear message |
| Binance API rejection | `BinanceClientError` with code + message |
| Network failure | `NetworkError` with details |
| Missing API credentials | Clean exit with instructions |

---

## Assumptions

- Targets **Binance Futures Testnet** (USDT-M) only — not real funds
- Symbols must end in `USDT` (e.g. `BTCUSDT`, `ETHUSDT`)
- Minimum quantity and price precision depend on the symbol's exchange filters
- `LIMIT` orders use `timeInForce=GTC` (Good Till Cancelled) by default

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for REST API calls |
| `python-dotenv` | Load API credentials from `.env` |