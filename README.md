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
├── cli.py                   # CLI entry point (argparse + interactive mode)
├── .env                     # API credentials (never committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/DeewakarBora/trading_bot.git
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

Get your credentials from [Binance Futures Testnet](https://testnet.binancefuture.com) — log in, go to the **API Key** tab, and click **Generate**.

---

## How to Run

### Option 1 — Interactive Mode (no arguments needed)

```bash
python cli.py
```

Launches a guided prompt that walks you through placing an order step by step with input validation and a confirmation step before placing.

### Option 2 — CLI Mode (pass arguments directly)

**Place a Market BUY order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Place a Market SELL order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

**Place a Limit BUY order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
```

**Place a Limit SELL order:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 2000
```

**View all options:**
```bash
python cli.py --help
```

---

## Example Output

### Interactive Mode
```
  ┌──────────────────────────────────────────┐
  │     Binance Futures Testnet Trading Bot  │
  │         Interactive Mode                 │
  └──────────────────────────────────────────┘

  No arguments detected — launching interactive mode.
  Press Ctrl+C at any time to exit.

  ❯  Symbol (default: BTCUSDT):
  ❯  Side [BUY/SELL]: BUY
  ❯  Order type [MARKET/LIMIT]: MARKET
  ❯  Quantity (e.g. 0.001): 0.001

  ┌─────────────────────────────────┐
  │         ORDER REQUEST            │
  ├─────────────────────────────────┤
  │  Symbol    : BTCUSDT             │
  │  Side      : BUY                 │
  │  Type      : MARKET              │
  │  Quantity  : 0.001               │
  │  Price     : MARKET              │
  └─────────────────────────────────┘

  ❯  Confirm and place order? [yes/no]: yes

  ┌─────────────────────────────────┐
  │         ORDER RESPONSE           │
  ├─────────────────────────────────┤
  │  Order ID  : 13057319797         │
  │  Status    : NEW                 │
  │  Exec Qty  : 0.001               │
  │  Avg Price : 0.00                │
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

## Bonus Feature

This project implements **Enhanced CLI UX** as the optional bonus:
- Running `python cli.py` with no arguments launches an interactive guided mode
- Step-by-step prompts with validation at each input
- Confirmation step before placing the order
- Clear error messages for invalid inputs

---

## Assumptions

- Targets **Binance Futures Testnet** (USDT-M) only — not real funds
- Symbols must end in `USDT` (e.g. `BTCUSDT`, `ETHUSDT`)
- Minimum quantity and price precision depend on the symbol's exchange filters
- `LIMIT` orders use `timeInForce=GTC` (Good Till Cancelled) by default
- Testnet API keys are generated from [testnet.binancefuture.com](https://testnet.binancefuture.com)

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for REST API calls |
| `python-dotenv` | Load API credentials from `.env` |
