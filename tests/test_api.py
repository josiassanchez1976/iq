import logging
from datetime import datetime, timedelta
import pytest

from ejtraderIQ import (
    IQOption,
    SymbolNotFoundError,
    OrderConflictError,
    APIUnavailableError,
)


def test_quote_and_history():
    api = IQOption('user', 'pass')
    quote = api.get_real_time_quote('EURUSD')
    assert quote is not None

    start = datetime.utcnow() - timedelta(minutes=2)
    end = datetime.utcnow()
    history = api.get_history('EURUSD', start, end)
    assert len(history) >= 1


def test_place_and_status_and_cancel():
    api = IQOption('user', 'pass')
    order_id = api.place_order('EURUSD', 'buy', 10)
    status, _ = api.check_order_status(order_id)
    assert status in {'win', 'loss', 'open'}
    if status == 'open':
        assert api.cancel_order(order_id) is True
        status, _ = api.check_order_status(order_id)
        assert status == 'cancelled'


def test_invalid_symbol():
    api = IQOption('user', 'pass')
    with pytest.raises(SymbolNotFoundError):
        api.get_real_time_quote('INVALID')


def test_order_errors():
    api = IQOption('user', 'pass')
    with pytest.raises(OrderConflictError):
        api.check_order_status(999)
    with pytest.raises(OrderConflictError):
        api.cancel_order(999)


def test_api_unavailable():
    api = IQOption('user', 'pass', fail_chance=1, max_retries=1)
    with pytest.raises(APIUnavailableError):
        api.get_real_time_quote('EURUSD')
