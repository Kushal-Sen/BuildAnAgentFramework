"""Python basics: values, decisions, loops and functions."""

# Values and variables
product = "Coffee"
price = 120
in_stock = True
print(product, price, in_stock)
print(type(product), type(price), type(in_stock))

# Working with values
total = price * 3
print(f"Three {product} orders cost {total}.")

# Decisions
if total >= 300:
    print("Big order")
elif total >= 100:
    print("Medium order")
else:
    print("Small order")

# Loops
for day in range(1, 4):
    print("Day", day)

orders_left = 3
while orders_left > 0:
    print("Orders left:", orders_left)
    orders_left = orders_left - 1


# Functions
def order_cost(price, quantity):
    """Return the cost of an order."""
    return price * quantity


def describe(product, cost):
    """Return a sentence about an order."""
    return f"{product} order: {cost}"


cost = order_cost(80, 2)
print(describe("Tea", cost))
