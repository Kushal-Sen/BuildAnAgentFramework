"""Price calculations."""


def order_total(price: float, quantity: int) -> float:
    """Return the cost of an order."""
    if quantity < 0:
        raise ValueError("quantity can't be negative")
    return price * quantity


def discounted(price: float, percent: float) -> float:
    """Return the price after a discount."""
    return price * (100 - percent) / 100
