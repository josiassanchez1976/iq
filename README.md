# ejtraderIQ

A minimal Python wrapper that mimics the behaviour of the IQ Option API.  This
library is intended for local development and testing and does not connect to
the real platform.  It exposes a small set of methods for obtaining quotes,
retrieving history, estimating payouts and placing mock orders.

## Installation

Python 3.9 or newer is required.  Install the package using pip:

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from datetime import datetime, timedelta
from ejtraderIQ import IQOption

api = IQOption("email", "password")
quote = api.get_real_time_quote("EURUSD")

start = datetime.utcnow() - timedelta(minutes=5)
end = datetime.utcnow()
history = api.get_history("EURUSD", start, end)

payout = api.get_payout_estimate("EURUSD")
order_id = api.place_order("EURUSD", "buy", 10)
status, result = api.check_order_status(order_id)
```

All methods return pandas `DataFrame` objects when the library is available,
otherwise lists of dictionaries are returned.

## Available Methods

- `get_real_time_quote(symbol)` – retrieve the latest quote
- `get_history(symbol, start_date, end_date)` – generate candle history
- `get_payout_estimate(symbol)` – return the payout percentage
- `stream_market_depth(symbol, callback)` – stream market depth once and
  call `callback` with the data
- `place_order(symbol, direction, amount)` – open a position
- `check_order_status(order_id)` – get current order state and result
- `cancel_order(order_id)` – cancel an open order

## Logging

All API activity is logged through the standard `logging` module using the
logger name `ejtraderIQ`.

## Disclaimer

This project is a simplified demonstration and **does not** interact with the
real IQ Option service.
