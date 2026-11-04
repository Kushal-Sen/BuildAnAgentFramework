import pytest

from shop.prices import discounted, order_total


def test_order_total():
    assert order_total(120, 2) == 240


def test_discounted():
    assert discounted(200, 25) == 150


def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        order_total(120, -1)
