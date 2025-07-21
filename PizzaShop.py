#Clarifying questions

#Pizza Management System

#Can users browse menu with different pizzas, sizes, and add-ons?
#What size : Multiple size types : small, medium, large : yes
#Will there be an options for users to select their own crust? type? thin crust. hand tossed, deep dish
#Will the users will be able to select their own toppins? 5 toppings for now
#Can users place orders and receive an order receipt?
#Can we support multiple orders at once (concurrency)?
#Do we allow delivery vs pickup options?
#Do we support payment processing? multiple types of payment 
#Are there any discounts/coupons?
# Is there an order tracking system (e.g., PREPARING → READY → DELIVERED)

#Size: Small, medium, large
#Crust: thin, deep, hand
#Topping: 5 types, price, description
#Order stauts
#Pizza, decide, size, crust, toppings, build function nested class, cal price
#Order: add items, calculate total, print reciept 

#🍕 Pizza Ordering System – Design Pitch (30–45 seconds)
#This system is built using Object-Oriented Design and incorporates both the Builder Pattern and Strategy Pattern to support customizable pizzas and flexible payments.
#I defined enums for Size, Crust, and Topping, each carrying its own price and label. This ensures extensibility and clean pricing logic.
#The Pizza class uses a nested Builder class, allowing fluent chaining to construct complex pizzas step-by-step.
#Each pizza calculates its price based on selected size, crust, and toppings. Toppings are stored in a Set to avoid duplication.
#The Order class holds multiple pizzas, supports delivery or pickup, and tracks order status through an OrderStatus enum (RECEIVED → PREPARING → READY → DELIVERED).
#For payments, I used the Strategy Pattern with classes like CardPayment, CashPayment, and UPIPayment. This keeps the design open for adding new payment types.
#The system prints a detailed receipt and allows status updates for order tracking.
#It's built to be modular, extensible, and easy to test, with support for concurrency or discounts being future additions.


from enum import Enum

# Step 1: Define Enums for fixed choices to make the code robust and readable.
# Each enum member holds its base price.
class Size(Enum):
    SMALL = (8.00, "Small")
    MEDIUM = (10.00, "Medium")
    LARGE = (12.00, "Large")
    
    def __init__(self, price, description):
        self.price = price
        self.description = description
        
class Crust(Enum):
    THIN = (2.00, "Thin Crust")
    HAND_TOSSED = (2.50, "Hand-Tossed")
    DEEP_DISH = (3.50, "Deep-Dish")
    def __init__(self, price, description):
        self.price = price
        self.description = description
    
class Topping(Enum):
    PEPPERONI = (1.50, "Pepperoni")
    MUSHROOMS = (1.00, "Mushrooms")
    ONIONS = (0.75, "Onions")
    EXTRA_CHEESE = (2.00, "Extra Cheese")
    TOMATO_SAUCE = (0.50, "Tomato Sauce")
    BASIL = (0.75, "Basil")
    
    def __init__(self, price, description):
        self.price = price
        self.description = description
        
class OrderStatus(Enum):
    RECEIVED = "Received"
    PREDPARING = "Preparing"
    READY = "Ready"
    DELIVERED = "Delivered"
    
class PaymentStrategy:
    def pay(self, amount: float):
        raise NotImplementedError()
    
class CashPayment(PaymentStrategy):
    def pay(self, amount: float):
        print(f"Paid ${amount:.2f} in Cash")
    
class CardPayment(PaymentStrategy):
    def pay(self, amount: float):
        print(f"Paid ${amount:.2f} using Credit/Debit card")

class CardPayment(PaymentStrategy):
    def pay(self, amount: float):
        print(f"Paid ${amount:.2f} using UPI.")
    
from typing import List, Set      
# Step 2: Define the Pizza class, which will be constructed by our Builder.
class Pizza:
    def __init__(self, builder):
        self.size: Size = builder.size
        self.crust: Crust = builder.crust
        self.toppings : Set[Topping] = builder.toppings
        
    def calculate_price(self) -> float:
        total = self.size.price + self.crust.price
        total += sum(t.price for t in self.toppings)
        return round(total, 2)
    
    """Provides a human-readable description of the pizza."""
    def __str__(self) -> str:
        description = f"- {self.size.description} {self.crust.description} Pizza (${self.calculate_price():.2f})\n"
        if self.toppings:
            description += "  Toppings: " + ", ".join(t.description for t in sorted(list(self.toppings), key=lambda t: t.name))
        return description
    
    # Step 3: Implement the Builder as a nested class.
    class Builder:
        def __init__(self):
            self.size = None
            self.crust = None
            self.toppings = Set()
            
        def with_size(self, size:Size):
            self.size = size
            return self
            
        def with_crust(self, crust:Crust):
            self.crust = crust
            return self
            
        def add_topping(self, topping:Topping):
            self.toppings.add(topping) 
            return self
            
        def build(self):
            if not self.size or not self.crust:
                raise ValueError("Pizza must have size and crust")
            return Pizza(self)
        
# Step 4: Define an Order class to hold items and calculate totals.
class Order:
    """Represents a customer's order, containing multiple items."""
    def __init__(self, order_id: int, customer_name : str, delivery_type = "Pickup"):
        self.order_id = order_id
        self.customer_name = customer_name
        self.delivery_type = delivery_type
        self.status = OrderStatus.RECEIVED
        self.items: List[Pizza] = []

    def add_item(self, item: Pizza):
        """Adds a configured pizza to the order."""
        self.items.append(item)

    def calculate_total(self) -> float:
        """Calculates the grand total for the order."""
        total = sum(item.calculate_price() for item in self.items)
        return round(total, 2)
    
    def update_status(self, new_status: OrderStatus):
        print(f"Order #{self.order_id} status updated from {self.status.value} to {new_status.value}")
        self.status = new_status
    
    def pay(self, payment_method: PaymentStrategy):
        total = self.calculate_total()
        payment_method.pay(total)

    def print_receipt(self):
        """Prints a detailed receipt for the order."""
        print(f"--- Order #{self.order_id} for {self.customer_name} ---")
        print(f"Delivery Type: {self.delivery_type}")
        print(f"Status: {self.status.value}")
        if not self.items:
            print("Order is empty.")
        else:
            for item in self.items:
                print(str(item))
        print("--------------------")
        print(f"Total: ${self.calculate_total():.2f}")
        print("--------------------")

# Step 6: The main application ties everything together.
# This demonstrates how a client would use your classes.
def main():
    """Main function to simulate placing an order at the pizza shop."""
    # Create a new order
    order = Order(order_id=101, customer_name = "Vaishnavi", delivery_type = "Delivery")
    
    # --- Add a custom-built pizza ---
    print("\nBuilding a custom pizza...")
    custom_pizza = Pizza.Builder()\
                        .with_size(Size.LARGE)\
                        .with_crust(Crust.DEEP_DISH)\
                        .add_topping(Topping.PEPPERONI)\
                        .add_topping(Topping.MUSHROOMS)\
                        .add_topping(Topping.ONIONS)\
                        .build()
    order.add_item(custom_pizza)
    
    
    # Print the final receipt
    print("\nFinal Order Details:")
    order.print_receipt()
    order.update_status(OrderStatus.PREDPARING)
    order.update_status(OrderStatus.READY)
    order.update_status(OrderStatus.DELIVERED)
    
    payment_method = CardPayment()
    order.pay(payment_method)


if __name__ == "__main__":
    main()
    
    
    
"""
With discount and threading 
from enum import Enum
from typing import List, Set
import threading

# Enums for Pizza configuration
class Size(Enum):
    SMALL = (8.00, "Small")
    MEDIUM = (10.00, "Medium")
    LARGE = (12.00, "Large")
    def __init__(self, price, description):
        self.price = price
        self.description = description

class Crust(Enum):
    THIN = (2.00, "Thin Crust")
    HAND_TOSSED = (2.50, "Hand-Tossed")
    DEEP_DISH = (3.50, "Deep Dish")
    def __init__(self, price, description):
        self.price = price
        self.description = description

class Topping(Enum):
    PEPPERONI = (1.50, "Pepperoni")
    MUSHROOMS = (1.00, "Mushrooms")
    ONIONS = (0.75, "Onions")
    EXTRA_CHEESE = (2.00, "Extra Cheese")
    TOMATO_SAUCE = (0.50, "Tomato Sauce")
    BASIL = (0.75, "Basil")
    def __init__(self, price, description):
        self.price = price
        self.description = description

# Pizza Class with Nested Builder
class Pizza:
    def __init__(self, builder):
        self.size = builder.size
        self.crust = builder.crust
        self.toppings = builder.toppings

    def calculate_price(self):
        price = self.size.price + self.crust.price
        price += sum(topping.price for topping in self.toppings)
        return round(price, 2)

    def __str__(self):
        description = f"- {self.size.description} {self.crust.description} Pizza (${self.calculate_price():.2f})\n"
        if self.toppings:
            description += "  Toppings: " + ", ".join(
                t.description for t in sorted(list(self.toppings), key=lambda t: t.name)
            )
        return description

    class Builder:
        def __init__(self):
            self.size = None
            self.crust = None
            self.toppings = set()

        def with_size(self, size: Size):
            self.size = size
            return self

        def with_crust(self, crust: Crust):
            self.crust = crust
            return self

        def add_topping(self, topping: Topping):
            self.toppings.add(topping)
            return self

        def build(self):
            if not self.size or not self.crust:
                raise ValueError("A pizza must have a size and a crust.")
            return Pizza(self)

# Order Class
class Order:
    lock = threading.Lock()

    def __init__(self, order_id: int):
        self.order_id = order_id
        self.items: List[Pizza] = []
        self.discount_code = None

    def add_item(self, item: Pizza):
        with Order.lock:
            self.items.append(item)

    def apply_coupon(self, code: str):
        valid_coupons = {"DISCOUNT10": 0.10, "FREESHIP": 5.00}
        if code in valid_coupons:
            self.discount_code = code
        else:
            print(f"Invalid coupon code: {code}")

    def calculate_total(self):
        total = sum(item.calculate_price() for item in self.items)
        if self.discount_code == "DISCOUNT10":
            total *= 0.90
        elif self.discount_code == "FREESHIP":
            total -= 5.00
        return round(max(total, 0), 2)

    def print_receipt(self):
        print(f"\n--- Order #{self.order_id} ---")
        if not self.items:
            print("Order is empty.")
        else:
            for item in self.items:
                print(str(item))
        print("--------------------")
        if self.discount_code:
            print(f"Coupon applied: {self.discount_code}")
        print(f"Total: ${self.calculate_total():.2f}")
        print("--------------------")

# Simulate one customer placing an order
def place_order(order_id: int):
    order = Order(order_id)
    pizza = Pizza.Builder()\
        .with_size(Size.MEDIUM)\
        .with_crust(Crust.HAND_TOSSED)\
        .add_topping(Topping.PEPPERONI)\
        .add_topping(Topping.EXTRA_CHEESE)\
        .build()
    order.add_item(pizza)

    if order_id == 101:
        order.apply_coupon("DISCOUNT10")
    elif order_id == 102:
        order.apply_coupon("FREESHIP")
    elif order_id == 103:
        order.apply_coupon("INVALID")  # test case

    order.print_receipt()

# Main function to simulate concurrent orders
def main():
    threads = []
    for i in range(3):
        t = threading.Thread(target=place_order, args=(101 + i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
"""