#Menu Size: Small, Medium , Large
#Fixed Toppings, choose any 
#Prize of pIza:


#Size: 
#Crust:
#Toppings
#Pizza - main 
#Order

from enum import Enum
class Size(Enum):
    SMALL = (8.00, "Small")
    MEDIUM = (10.00, "Medium")
    LARGE = (12.00, "Large")
    
    def __init__(self, price, description):
        self.price = price
        self.description = description
        
class Crust(Enum):
    HAND_TOSSED = (2.50, "Hand-Tossed")
    CHEESY = (3.00, "Cheesy")
    THIN_CRUST = (4.00, "Thin-Crust")
    DEEP_DISH = (5.00, "Deep-Dish")
    
    def __init__(self, price, description):
        self.price = price
        self.description = description


class Toppings(Enum):
    ONION = (1.50, "Onions")
    TOMATOES = (1.50, "Tomatoes")
    OLIVES = (2.00, "Olives")
    PEPPERONI = (4.00, "Pepperoni")
    BASIL = (2.00, "Basil")
    
    def __init__(self, price, description):
        self.price = price
        self.description = description
        
from typing import Set
class Pizza:
    def __init__(self, size: Size, crust : Crust, toppings: Set[Toppings]):
        self.size = size
        self.crust = crust
        self.toppings = toppings
        
    """
    def __init__(self, builder):
        self.size: Size = builder.size
        self.crust: Crust = builder.crust
        self.toppings: Set[Topping] = builder.toppings
    """
        
    def cal_price(self) -> float:
        base = self.crust.price + sum(t.price for t in self.toppings)
        price = base * self.size.price
        return round(price, 2)
    """
    class Builder:
        def __init__(self):
            self.size = None
            self.crust = None
            self.toppings = set()
        def with_size(self, s): self.size = s; return self
        def with_crust(self, c): self.crust = c; return self
        def add_topping(self, t): self.toppings.add(t); return self
        def build(self):
            if not self.size or not self.crust:
                raise ValueError("Need size & crust")
            return Pizza(self.size, self.crust, self.toppings)
            
p = Pizza.Builder()\
      .with_size(Size.MEDIUM)\
      .with_crust(Crust.THIN)\
      .add_topping(Topping.OLIVE)\
      .build()
    """
def main():
    p = Pizza(Size.LARGE, Crust.CHEESY, {Toppings.OLIVES, Toppings.ONION})
    print(p.price())
    
    """
    print("\nBuilding a custom pizza...")
    custom_pizza = Pizza.Builder()\
                        .with_size(Size.LARGE)\
                        .with_crust(Crust.DEEP_DISH)\
                        .add_topping(Topping.PEPPERONI)\
                        .add_topping(Topping.MUSHROOMS)\
                        .add_topping(Topping.ONIONS)\
                        .build()
    """

if __name__ == "__main__":
    main()
        