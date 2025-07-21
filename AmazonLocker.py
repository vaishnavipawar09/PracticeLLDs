#Clarifying Questions

#Size of packages and Lockers? yes  small, medium, large
#Can i assume that the package shoullf go to the corresponding locker size? yes
# What if no small locker but a small package? shift to store it in locker  +1 size ie medium
#what if a package arrives and there is no valid locker available? pickup not accepted
#how does the customer retrieve their package? do they receive a pin? is it unique? yes
#What if pin is wrong and locker empty? action fails
#Multiple locations each with sets of locker of different locker counts? yes
#Auto assigned to nearest location
#customers able to open only their lockers, and package should be securely stored and accessible to its customer only ? yes
#Should it be a scalable and extensible system? yes
# Customers get notified about assigned lockers or faileure? yes


#Package size: enum small, medium ,large
#Locker: assign, free, addobserver, remove_observer, notifyobserver, checkpin
#Customer: receive the mag, unassignlocker, 
#Location: coordinates
#Calculate distance: euclideon  
#AmazonLockerSystem:(main class) addloc, closestloc, assignlocker

# ✅ Verbal Design Pitch: Amazon Locker System
# We are designing an Amazon Locker Management System that:
# - Supports multiple locations, each with its own lockers
# - Supports locker sizes (SMALL, MEDIUM, LARGE)
# - Assigns lockers based on proximity and availability
# - Escalates locker size if perfect fit not available
# - Uses PINs for secure access
# - Notifies customers via Observer pattern
# - Calculates nearest locker using Strategy pattern
# - Follows Singleton pattern for centralized system control

# Classes:
# 1. Enum: PackageSize - Defines SMALL, MEDIUM, LARGE
# 2. Class: Locker - Tracks locker size, assignment status, and assigned PIN
# 3. Class: Customer - Stores customer info, tracks assigned locker and updates via observer
# 4. Class: Location - Represents a pickup location with coordinates and lockers
# 5. Interface: DistanceCalculationStrategy - Strategy pattern base
# 6. Class: EuclideanDistanceStrategy - Concrete strategy
# 7. Class: AmazonLockerSystem (Singleton) - Manages all locations, assigns lockers

from enum import Enum
class PackageSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Locker:
    def __init__(self, locker_id: int, size: PackageSize):
        self.locker_id = locker_id
        self.size = size
        self.pin = None
        self.is_assigned = False
        self.observers = set()
        
    def assign(self, pin : int):
        self.is_assigned = True
        self.pin = pin
        self.notify_observer()
    
    def free(self):
        self.is_assigned = False
        self.pin = None
    
    def add_observer(self, observer):
        self.observers.add(observer)
        
    def remove_observer(self, observer):
        self.observers.remove(observer)
        
    def notify_observer(self):
        for observer in self.observers:
            observer.update(self.locker_id, self.pin)
    
    def check_pin(self, pin : int) -> bool:
        return self.is_assigned and self.pin ==pin

class Customer:
    def __init__(self, customer_id : int , latitude: float, longitude: float):
        self.customer_id = customer_id
        self.latitude = latitude
        self.longitude = longitude
        self.assigned_locker = None
        self.pin = None
        
    def update(self, locker_id: int, pin : int):
        self.assigned_locker = locker_id 
        self.pin = pin
        print(f" Customer {self.customer_id}: Assigned locker ID -{locker_id} with pin {pin} ")
        
     # Method to order a package and assign locker
    def order_package(self, package: PackageSize, amazon_locker_system):
        amazon_locker_system.assign_locker(self, package)

    def unassign_locker(self, pin: int) -> bool:
        if self.assigned_locker and self.assigned_locker.check_pin(pin):            #check if assigned locker and th epin matches
            self.assigned_locker.free()
            self.assigned_locker = None
            self.pin = None
            print(f"Customer {self.customer_id}: Locker unassigned successfully")
            return True
        else:
            print(f"Customer {self.customer_id}: Invalid PIN or no assigned locker")
            return False

# Strategy Interface for distance calculation
class DistanceCalculationStrategy:
    def calculate_distance(self, loc1_latitude: float, loc1_longitude: float, loc2_latitude: float, loc2_longitude: float) -> float:
        pass

import math
import random
# Concrete Strategy for Euclidean distance calculation
class EuclideanDistanceStrategy(DistanceCalculationStrategy):
    def calculate_distance(self, loc1_latitude: float, loc1_longitude: float, loc2_latitude: float, loc2_longitude: float) -> float:
        return math.sqrt((loc1_latitude - loc2_latitude) ** 2 + (loc1_longitude - loc2_longitude) ** 2)   #sqrt ((x1 - x2)^2 + (y1 - y2)^2)

class AmazonLockerSystem:
    _instance = None
    
    def __new__(cls, strategy: DistanceCalculationStrategy):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.locations = []
            cls._instance.strategy = strategy
        return cls._instance
    
    def add_location(self, location):
        self.locations.append(location)
    
    # Method to find the closest location to the customer
    def find_closest_location(self, customer_latitude: float, customer_longitude: float):
        closest_location = None
        min_distance = float('inf')

        for location in self.locations:
            distance = self.strategy.calculate_distance(location.latitude, location.longitude, customer_latitude, customer_longitude)
            if distance < min_distance:
                min_distance = distance
                closest_location = location

        return closest_location      
    
    # Method to assign a locker to the customer for a given package
    def assign_locker(self, customer, package_size: PackageSize) -> bool:
        escalation_order = {
        PackageSize.SMALL: [PackageSize.SMALL, PackageSize.MEDIUM, PackageSize.LARGE],
        PackageSize.MEDIUM: [PackageSize.MEDIUM, PackageSize.LARGE],
        PackageSize.LARGE: [PackageSize.LARGE]
        }
        
        closest_location = self.find_closest_location(customer.latitude, customer.longitude)
        if closest_location:
            for size in escalation_order[package_size]:
                for locker in closest_location.lockers:
                    if not locker.is_assigned and locker.size == size:
                        pin = random.randint(100000, 999999)
                        locker.assign(pin)
                        customer.assigned_locker = locker
                        customer.pin = pin
                        locker.add_observer(customer)
                        return True
        print(f"Customer {customer.customer_id}: No suitable locker available.")
        return False

# Location class representing a location with multiple lockers
class Location:
    def __init__(self, latitude: float, longitude: float, lockers: list):
        self.latitude = latitude
        self.longitude = longitude
        self.lockers = lockers  