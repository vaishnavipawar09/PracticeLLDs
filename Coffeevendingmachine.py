# Types: Expresso, cappuccino, Ltte
# Type of coffe vary by , price, recipe
# Display, the opyions and price
# user select coffee type and pay
# Dispense the certain product and return change if any ? yes
# keep of track of products, quantities? yes
# Multiple Transactions concurrently, yes, ensure thread safety

# Coffee Products: expresso, cappuccino, latte- Enum
# Payment 
# Ingredients= track, quanity
# CoffeeMachine i smain, single instance - 
# displaymenu, selectcoffee, make payment, dispense, update ingredietents quantities
\
    
    
class Coffee:
    def __init__(self, name, price, recipe):
        self.name = name
        self.price = price
        self.recipe = recipe
        
       
    def get_name(self):
        return self.name
    
    def get_price(self):
        return self.price
 
    
    def get_recipe(self):
        return self.recipe
    
class Payment:
    def __init__(self, amount):
        self.amount = amount
        
    def get_amount(self):
        return self.amount
    
class Ingredient:
    def __init__(self, name, quantity):
        self.name = name
        self.quanity = quantity
    
    def get_name(self):
        return self.name

    def get_quantity(self):
        return self.quantity
    
    def update_quantity(self, amount):
        self.quanity += amount
    
class CoffeeMachine:
    _instance = None
    
    def __init__(self):
        if CoffeeMachine._instance is not None: 
            raise Exception("Class is singleton")
        else:
            CoffeeMachine._instance = self
            self.coffee_menu = []
            self.ingredients = {}
            self._initialize_coffee_menu()
            self._initialize_ingredients()
            
    @staticmethod
    def get_instance():
        if CoffeeMachine._instance is None:
            CoffeeMachine()
        return CoffeeMachine._instance
    
    
    def _initialize_coffee_menu(self):
        expresso_recipe = {
            self.ingredients["Coffee"]: 1,
            self.ingredients["Water"]: 1,
        }
        self.coffee_menu.append(Coffee("Expresso", 2.5, expresso_recipe))
    
    def _initialize_coffee_menu(self):
        cappuccino_recipe = {
            self.ingredients["Coffee"]: 1,
            self.ingredients["Water"]: 1,
            self.ingredients["Milk"]: 1,
        }
        self.coffee_menu.append(Coffee("Cappuccino", 3.5, cappuccino_recipe))
    
    def _initialize_coffee_menu(self):
        latte_recipe = {
            self.ingredients["Coffee"]: 1,
            self.ingredients["Water"]: 1,
            self.ingredients["Milk"]: 1,
        }
        self.coffee_menu.append(Coffee("Latte", 4.5, latte_recipe))
    
    def _initialize_ingredients(self):
        self.ingredients["Coffee"] = Ingredient("Coffee", 10)
        self.ingredients["Water"] = Ingredient("Water", 10)
        self.ingredients["Milk"] = Ingredient("Milk", 10)
        
        
    
    def diplay_menu(self):
        print("coffe menu:")
        for coffee in self.coffee_menu:
            print(f"{Coffee.get_name()} - ${coffee.get_price()}")
    
        
    def select_coffee(self, coffee_name):
        for coffee in self.coffee_menu:
            if coffee.get_name().lower() == coffee_name.lower():
                return coffee
        return None   
    
    def dispense_coffee(self, coffee, payment):
        if payment.get_amount() >= coffee.get_price():
            if self._has_enough_ingredients(coffee):
                self._update_ingredients(coffee)
                print(f"Dispensing {coffee.get_name()}...")
                change = payment.get_amount() - coffee.get_price()
                if change > 0:
                    print(f"Please collect your change: ${change}")
            else:
                print(f"Insufficient ingredients to make {coffee.get_name()}")
        else:
            print(f"Insufficient payment for {coffee.get_name()}")

    def _has_enough_ingredients(self, coffee):
        for ingredient, required_quantity in coffee.get_recipe().items():
            if ingredient.get_quantity() < required_quantity:
                return False
        return True

    def _update_ingredients(self, coffee):
        for ingredient, required_quantity in coffee.get_recipe().items():
            ingredient.update_quantity(-required_quantity)
            if ingredient.get_quantity() < 3:
                print(f"Low inventory alert: {ingredient.get_name()}")
    
