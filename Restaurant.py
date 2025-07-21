#Clarifying Questions: Restaurant management system

#Allow customers to view menu, place order and make reservation? yes
#Manage the restaurants inventory, ingredients, and menu items
#Can menu items, be adjusted according to the stock? 
#should handle order processing, including order preparation, billing, and payment.
#Multiple payment types? yes, cash , card and mobile payment
# should manage staff information, including roles, schedules, and performance tracking.
#generate reports and analytics for management, such as sales reports and inventory analysis.
#The system should handle concurrent access and ensure data consistency.

# ✅ Verbal Design Pitch: Restaurant Management System

# We’re building a centralized Restaurant Management System (RMS) with these core capabilities:
# • Menu Management: add/remove MenuItem; each item has ID, name, description, price, availability.
# • Order Processing: place Order (PENDING→PREPARING→READY→COMPLETED/CANCELLED), track items, totals, timestamp.
# • Reservations: manage Reservation lifecycle—create, modify, cancel.
# • Payments: process Payment with PaymentMethod (CASH, CREDIT_CARD, MOBILE), track PaymentStatus.
# • Staff Management: manage Staff roster with roles and contact details.
# • Thread-safety: use thread-safe structures or locks for shared data (orders, reservations, menu).
# • Notifications: placeholder methods (_notify_kitchen, _notify_staff) to alert relevant parties.

# Key Classes & Methods:
# – MenuItem: represents an eatable; getters for all properties.
# – Order & OrderStatus: holds list of MenuItem, total_amount, status transitions via set_status().
# – Reservation: (not shown) would track customer, party_size, timeslot.
# – Payment & Enums: manage payment flow and status.
# – Staff: holds ID, name, role, contact.
# – Restaurant (Singleton):
#    • add_menu_item/remove_menu_item/get_menu()
#    • place_order(order) → stores order + notify kitchen
#    • update_order_status(id, status) → notifies staff
#    • make_reservation/cancel_reservation()
#    • process_payment()
#    • add_staff/remove_staff()
#    • Uses a single thread-safe instance to coordinate all operations.

# Design Patterns Employed:
# – Singleton Pattern on Restaurant: ensures one global system instance.
# – Enum Pattern for status and method types: makes statuses and payment methods self-documenting.
# – (Optional) Observer or Pub/Sub for kitchen/staff notifications: decouples event producers from consumers.
# – Strategy Pattern could be layered later for flexible pricing or reporting algorithms.

# This architecture cleanly separates concerns, supports thread-safe concurrent access, and is extensible
# for future requirements like table assignment, ingredient inventory tracking, or external integrations.


#OrderStatus
# Order 
#MenuItem
# Paymentmethod
#Payment Status
#payment 
#staff
#Restaurant


from enum import Enum
from datetime import datetime

class OrderStatus(Enum):
    PENDING = 1
    PREPARING = 2
    READY = 3
    COMPLETED = 4
    CANCELLED = 5
    

class Order:            #all get funt in the order method
    def __init__(self, id, items, total_amount, status, timestamp):
        self.id = id
        self.items = items
        self.total_amount = total_amount
        self.status = status
        self.timestamp = timestamp
        
    def set_status(self, status):
        self.status = status

    def get_id(self):
        return self.id

    def get_items(self):
        return self.items

    def get_total_amount(self):
        return self.total_amount

    def get_status(self):
        return self.status

    def get_timestamp(self):
        return self.timestamp
    

class MenuItem:          #all get funt in the order method
    def __init__(self, id, name, description, price, available):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.available = available

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_price(self):
        return self.price

    def is_available(self):
        return self.available()
    
class PaymentMethod(Enum):
    CASH = 1
    CREDIT_CARD = 2
    MOBILE_PAYMENT = 3
    
class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    
    
class Payment:              ##all get funt in the order method
    def __init__(self, id, amount, method, status):
        self.id = id
        self.amount = amount
        self.method = method
        self.status = status

    def get_id(self):
        return self.id

    def get_amount(self):
        return self.amount

    def get_method(self):
        return self.method

    def get_status(self):
        return self.status
    
class Reservation:
    def __init__(self, id, customer_name, contact_number, party_size, reservation_time):
        self.id = id
        self.customer_name = customer_name
        self.contact_number = contact_number
        self.party_size = party_size
        self.reservation_time = reservation_time
    
class Staff:
    def __init__(self, id, name, role, contact_number):
        self.id = id
        self.name = name
        self.role = role
        self.contact_number = contact_number
        
from concurrent.futures import ThreadPoolExecutor

class Restaurant:
    _instance = None
    _lock = ThreadPoolExecutor(max_workers=1)
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    """Two threads might both see “no instance” at almost the same time and race to grab that lock. 
    Once one thread holds the lock and creates the instance, the inner check prevents the second thread (which will unblock on the same lock) from creating a second instance.
    So the two checks together give us both high performance (avoiding unnecessary locks once initialized) and correctness (only one instance even under concurrent access)."""
    

    def _initialize(self):
        self.menu = []
        self.orders = {}
        self.reservations = []
        self.payments = {}
        self.staff = []

    def add_menu_item(self, item):
        self.menu.append(item)

    def remove_menu_item(self, item):
        self.menu.remove(item)

    def get_menu(self):
        return self.menu[:]

    def place_order(self, order):
        self.orders[order.get_id()] = order
        self._notify_kitchen(order)

    def update_order_status(self, order_id, status):
        order = self.orders.get(order_id)
        if order:
            order.set_status(status)
            self._notify_staff(order)

    def make_reservation(self, reservation):
        self.reservations.append(reservation)

    def cancel_reservation(self, reservation):
        self.reservations.remove(reservation)

    def process_payment(self, payment):
        self.payments[payment.get_id()] = payment

    def add_staff(self, staff):
        self.staff.append(staff)

    def remove_staff(self, staff):
        self.staff.remove(staff)

    def _notify_kitchen(self, order):
        pass

    def _notify_staff(self, order):
        pass
    
    
    





"""ine-by-Line Commentary (separate from the code)

from enum import Enum
Import Python’s Enum base class so we can define strongly-typed status and method constants.

from datetime import datetime
Import datetime for timestamping orders, comments, or reservations.

class OrderStatus(Enum):
PENDING, PREPARING, READY, COMPLETED, CANCELLED
Define every possible state an order may occupy—helps avoid magic strings and enforces valid transitions.

class Order:
__init__(self, id, items, total_amount, status, timestamp)
Constructor captures order’s unique ID, its line-items (MenuItem list), the precomputed total, its starting OrderStatus, and when it was created.

set_status(self, status)
Mutator to update an order’s lifecycle state (e.g. from PENDING→PREPARING).

get_id(), get_items(), get_total_amount(), get_status(), get_timestamp()
Simple accessors so external code can retrieve order metadata without directly touching internals.

class MenuItem:
__init__(self, id, name, description, price, available)
Constructor captures the menu entry’s ID, display name, descriptive text, unit price, and a boolean flag for on/off-menu.

get_id(), get_name(), get_description(), get_price(), is_available()
Accessors—is_available() returns whether this item can currently be ordered.

class PaymentMethod(Enum):
CASH, CREDIT_CARD, MOBILE_PAYMENT
Enumerates all supported ways a customer may pay.

class PaymentStatus(Enum):
PENDING, COMPLETED, FAILED
Represents the result of a payment attempt.

class Payment:
__init__(self, id, amount, method, status)
Constructor captures a payment’s unique ID, the dollar amount, which PaymentMethod was used, and its PaymentStatus.

get_id(), get_amount(), get_method(), get_status()
Accessors for external reporting or reconciliation.

class Reservation:
__init__(self, id, customer_name, contact_number, party_size, reservation_time)
Simple data holder for a table reservation: reservation ID, guest name/phone, party count, and desired time.

class Staff:
__init__(self, id, name, role, contact_number)
Represents an employee with a unique ID, name, functional role (e.g. “Chef”, “Waiter”), and contact.

class Restaurant (Singleton)
_instance = None
Class-level storage for the one and only Restaurant instance.

_lock = ThreadPoolExecutor(max_workers=1)
Using a single-worker executor as a mutex to safely initialize the singleton. (Double-checked locking pattern.)

def __new__(cls): …
Override object creation so the first caller constructs the one instance, and everyone else reuses it.

First if not cls._instance:
Fast-path check—if instance already exists, skip locking entirely.

with cls._lock:
Acquire our single-thread executor lock to prevent two threads racing to build the instance.

Second if not cls._instance inside lock:
Ensures that once Thread A has constructed the instance, Thread B (unblocked on the same lock) does not build a second copy.

cls._instance = super().__new__(cls) + _initialize():
Allocate the new object and populate its core data structures exactly once.

def _initialize(self):
self.menu = []
List of all MenuItem objects currently offered.

self.orders = {}
Map from order ID → Order, for quick lookup and updates.

self.reservations = []
List of all active Reservation instances.

self.payments = {}
Map from payment ID → Payment, so we can audit or retry payments.

self.staff = []
Roster of Staff objects with their roles.

Core Methods on Restaurant:
add_menu_item(item) / remove_menu_item(item)
Dynamically update the available menu.

get_menu()
Return a shallow copy of the menu list to prevent callers from mutating internal state.

place_order(order)
Store a new Order and immediately call _notify_kitchen() so chefs get alerted.

update_order_status(order_id, status)
Look up an existing order, change its OrderStatus, then call _notify_staff() so waiters or managers know.

make_reservation(reservation) / cancel_reservation(reservation)
Add or remove table bookings from our in-memory list.

process_payment(payment)
Record the result of a Payment attempt.

add_staff(staff) / remove_staff(staff)
Manage the employee roster as people join or leave.

_notify_kitchen(order) / _notify_staff(order)
Placeholders for pushing updates—could hook into Observer pattern, messaging queue, or direct method calls.

Design Patterns & Rationale:

Singleton for Restaurant ensures a single source of truth for menu, orders, reservations, payments, and staff.

Enum classes (OrderStatus, PaymentMethod, PaymentStatus) guarantee we only use valid, self-documenting constants.

Double-Checked Locking around __new__() balances thread-safety of lazy initialization with minimal synchronization overhead.

Separation of Concerns: Data classes (Order, MenuItem, Payment, etc.) only hold state and simple accessors, while Restaurant orchestrates business operations.

Extensible Hooks (_notify_kitchen, _notify_staff) set us up for future Observer or Pub/Sub integration without changing core logic."""