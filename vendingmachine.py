# Clarifying Questions to ask!

# Multiple products? yes
# Multiple quantities? yes
# Mutiple types payments coins , cash? yes
# Dispense the certain product and return change if any ? yes
# keep of track of products, quantities? yes
# Multiple Transactions concurrently, ensure data consistency? no
# Interface to restock the product and collecting the money? yes
# Insufficient funds or out of stock? yes


# Product: Multiple items
# Coin, Note = Enum
# Inventory = map the product , quantity 
# VendingMachineState (ABC):  Idle, Ready, Dispense
# VendingMachine: main class, one instance - Current, SlectedProduct, Total payments, Payment handlind


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

from enum import Enum
        
class Coin(Enum):
    Penny = 0.01
    Nickel = 0.05
    Dime = 0.1
    Quarter = 0.25
    
class Notes(Enum):
    One = 1
    Five = 5
    Ten = 10
    Twenty = 20

#“I used Enum for Coin and Note to restrict accepted denominations to only valid values. This avoids magic numbers, helps validation, and ensures compile-time safety with clear names like PENNY or FIVE_DOLLAR instead of raw values.”

#Quick Summary of Why enum is Used- Prevents magic numbers, Allows validation via switch/case or value lookup
#Easy to add new denominations, Ensures only valid input is used at compile time   

class Inventory:
    def _init__(self):
        self.products = {}
        
    def is_available(self, product):
        return product in self.products and self.products[product] > 0
        
    def add_product(self, product, quantity):
        self.products[product] = quantity
        
    def remove_product(self, product):
        del self.products[product]
    
    def update_quantity(self, product, quantity):
        self.products[product] = quantity
   
    def get_quantity(self, product):
        return self.products.get(product, 0)
    
from abc import ABC, abstractmethod

class VendingMachineState(ABC):
    def __init__(self, vending_machine):
        self.vending_machine = vending_machine
        
    @abstractmethod
    def select_product(self, product):
        pass
     
    @abstractmethod
    def insert_coin(self, coin):
        pass
    
    @abstractmethod
    def insert_note(self, note):
        pass

    @abstractmethod
    def dispense_product(self):
        pass

    @abstractmethod
    def return_chnage(self):
        pass
        

class IdleState(VendingMachineState):
    def __init__(self, vending_machine):
        super().__init__(vending_machine)
        
    def select_product(self, product: Product):
        if self.vending_machine.inventory.is_available(product):
            self.vending_machine.selected_product = product
            self.vending_machine.set_state(self.vending_machine.ReadyState)
            print("Product Selected: {product.name}")
        else:
            print("Product not available: {product.name}")
            
    
    def insert_coin(self, coin: Coin):
        print("Please select a product")
        
    def insert_note(self, note: Notes):
        print("Please select a product")
    
    def dispense_product(self):
        print("Please select a product and make payment.")

    def return_change(self):
        print("No change to return.")
        
class ReadyState(VendingMachineState):
    def __init__(self, vending_machine):
        super().__init__(vending_machine)
        
    def select_product(self, product: Product):
        print("Product already selected. Please make payment.")
    
    def insert_coin(self, coin: Coin):
        self.vending_machine.add_coin(coin)
        print(f"Coin inserted: {coin.name}")
        self.checkpaymentstatus()
        
    def insert_note(self, note: Notes):
        self.vending_machine.add_note(note)
        print(f"Note inserted: {note.name}")
        self.checkpaymentstatus()
        
    def dispense_product(self):
        print("Please make payment first.")
    
    def return_change(self):
        print("Please wait until product is dispensed")
                
    def checkpaymentstatus(self):
        if self.vending_machine.total_payment >= self.vending_machine.selected_product.price:
            self.vending_machine.set_state(self.vending_machine.DispenseState)
            
        
class DispenseState(VendingMachineState):
    def __init__(self, vending_machine):
        super().__init__(vending_machine)
    
    def select_product(self, product: Product):
        print("Product already selected. Please collect the dispensed product.")

    def insert_coin(self, coin: Coin):
        print("Payment already made. Please collect the dispensed product.")

    def insert_note(self, note: Notes):
        print("Payment already made. Please collect the dispensed product.")
        
    def dispense_product(self):
        self.vending_machine.set_state(self.vending_machine.ReadyState)
        product = self.vending_machine.selected_product
        self.vending_machine.inventory.update_quantity(product, self.vending_machine.inventory.get_quantity(product) - 1)
        print(f"Product Dispensed: {product.name}")
        self.vending_machine.return_change()
        
    def return_change(self):        
        change = self.vending_machine.total_payment - self.vending_machine.selected_product.price
        if change > 0:
            print(f"Change returned: ${change:.2f}")
            self.vending_machine.reset_payment()
            self.vending_machine.selected_product = None
        else:
            print(f"No change to return")
        self.vending_machine.set_state(self.vending_machine.idle_state)

    
from threading import Lock
                
class VendingMachine:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.inventory = Inventory()
                cls._instance.IdleState = IdleState(cls._instance)
                cls._instance.ReadyState = ReadyState(cls._instance)
                cls._instance.DispenseState = DispenseState(cls._instance)
                cls._instance.current_state = cls._instance.IdleState
                cls._instance.selected_product = None
                cls._instance.total_payment = 0.0
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        return cls()
    
    def select_product(self, product: Product):
        self.current_state.select_product(product)

    def insert_coin(self, coin: Coin):
        self.current_state.insert_coin(coin)

    def insert_note(self, note: Notes):
        self.current_state.insert_note(note)

    def dispense_product(self):
        self.current_state.dispense_product()

    def return_change(self):
        self.current_state.return_change()
    
    def set_state(self, state: VendingMachineState):
        self.current_state = state
        
    def add_coin(self, coin: Coin):
        self.total_payment += coin.value

    def add_note(self, note: Notes):
        self.total_payment += note.value
        
    def reset_payment(self):
        self.total_payment = 0.0
                 
        


#Optional : For Restock and Money take
#Updated Inventory class with restock support
#Add this method to your existing Inventory class:

def restock_product(self, product, quantity):
    if product in self.products:
        self.products[product] += quantity
    else:
        self.products[product] = quantity
    print(f"Restocked {product.name}: +{quantity} units. Total: {self.products[product]}")
    
#Extend VendingMachine class to support restocking & collecting money

class VendingMachine:
    _instance = None
    _lock = Lock()
    _collected_money = 0.0  # Track total collected cash

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._collected_money = 0.0
        return cls._instance

    # Existing methods...

    def restock(self, product: Product, quantity: int):
        self.inventory.restock_product(product, quantity)

    def collect_money(self):
        print(f"Collected ${self._collected_money:.2f} from the machine.")
        self._collected_money = 0.0  # Reset after collection

    def add_coin(self, coin: Coin):
        self.total_payment += coin.value
        self._collected_money += coin.value  # Track for collection

    def add_note(self, note: Notes):
        self.total_payment += note.value
        self._collected_money += note.value
        
        
#Summary & Dry Run
"""
VENDING MACHINE SYSTEM DESIGN

This Vending Machine system uses the State Design Pattern with three primary states:
- IdleState
- ReadyState
- DispenseState

🧠 DESIGN OVERVIEW:
- Products are represented using a `Product` class and tracked with quantities in a centralized `Inventory`.
- Accepted denominations (coins and notes) are implemented using Python Enums to restrict input to valid values only.
- The machine supports inserting coins and cash (notes), tracking payments against selected product price.

🔁 WORKFLOW:
1. User starts in IdleState and selects a product.
2. If available, machine transitions to ReadyState and awaits payment.
3. Once total payment is ≥ product price, machine moves to DispenseState.
4. Product is dispensed, change (if any) is returned, and machine resets to IdleState.

🛠️ KEY PATTERNS & PRINCIPLES:
- State Pattern: Clearly models machine behavior in each state.
- Singleton Pattern: Ensures only one VendingMachine instance exists.
- Enum Usage: Prevents invalid payment values and promotes type safety.

✅ The design is modular, readable, and compliant with all functional requirements.
"""
