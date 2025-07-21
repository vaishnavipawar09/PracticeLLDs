# Clarifying Questions to ask!

# Vehicle types : car, truck, motorcycle
# no. of floors/ level: multiple levels,  identical: yes
# certain number of parking slot at each level: yes
# parking spot will it vary by size : yes, supports specufic ty[e of vehicle: yes
# system assign nearest slot or any free slot ?
# slot is reserved during entry and released during exit 
# Track the availabiloity of parking spot and provide real time info to custometer? display board or mobile app
# Mutliple entry and exit points and support concurrents access 
# how about payment ? is it a flat rate or duration rate? done at entry or exit ? 
# online reservation and pre booking?
# vehicle registration/ license tracking
# admin functionality? 


# ParkingLot : one instance of parking lot exists
# Level: level, list of parking spots
# ParkingSpots: individual parking spot, vehicle type/ size, availability
# Vehicle (ABC),different types 
# VehicleType :  var, trucks, bike
# Ticket
# PricingStrategy
# Gate

from abc import ABC
from enum import Enum

class VehicleType(Enum):
    CAR = 1
    MOTORCYCLE = 2
    TRUCK = 3
    
class Vehicle(ABC):
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.type = vehicle_type
            
    def get_type(self) -> VehicleType:
        return self.type
        
class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)
   
        
class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)

class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)
        
class ParkingSpot:
    def __init__(self, spot_number: int):
        self.spot_number = spot_number
        self.vehicle_type = VehicleType.CAR  
        self.parked_vehicle = None   
        
    def is_available(self) -> bool:
        return self.parked_vehicle is None   
    
    def park_vehicle(self, vehicle: Vehicle) -> None:
        if self.is_available() and vehicle.get_type() == self.vehicle_type:
            self.parked_vehicle = vehicle
        else:
            raise ValueError("Invalid vehicle typr or spot already full")
        
    def unpark_vehicle(self)-> None:            #Unpark after use of spot
        self.parked_vehicle = None
        
    def get_vehicle_type(self) -> VehicleType:          #write this for level class
        return self.vehicle_type
    
    def get_parked_vehicle(self) -> VehicleType:        #write this for vehicle class
        return self.parked_vehicle     
    
    def get_spot_number(self) -> int:                   #Needed while displaying info
        return self.spot_number
    
  
from typing import List
  
class Level:
    def __init__(self, floor: int, num_spot: int):
        self.floor = floor
        self.parking_spots = List[ParkingSpot] = [ParkingSpot(i) for i in range(num_spot)]
        
    def park_vehicle(self, vehicle : Vehicle) -> bool:
        for spot in self.parking_spots:
            if spot.is_available() and spot.get_vehicle_type() == vehicle.get_type():
                spot.park_vehicle(vehicle)
                return True
        return False
    
    def unpark_vehicle(self, vehicle : Vehicle) -> bool:
        for spot in self.parking_spots:
            if not spot.is_available() and spot.get_parked_vehicle() == vehicle:
                spot.unpark_vehicle()
                return True
        return False     
        
    def display_availability(self) -> None:
        print(f"Level {self.floor} Availability:")
        for spot in self.parking_spots:
            print(f"Spot {spot.get_spot_number()}: {'Available' if spot.is_available() else 'Occupied'}")
            

class ParkingLot:
    _instance = None
    
    def __init__(self):
        if ParkingLot._instance is not None:
            raise Exception("This class is singleton")
        else:
            ParkingLot._instance = self
            self.levels: List[Level] = []
            
    @staticmethod
    def get_instance():
        if ParkingLot._instance is None:
            ParkingLot()
        return ParkingLot._instance
    
    #Not required but remember
    def add_level(self, level: Level) -> None:
        self.levels.append(level)
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        for level in self.levels:
            if level.park_vehicle(vehicle):
                return True
        return False
    
    def unpark_vehicle(self, vehicle: Vehicle) -> bool:
        for level in self.levels:
            if level.unpark_vehicle(vehicle):
                return True
        return False
    
    def display_availability(self) -> None:
        for level in self.levels:
            level.display_availability()
            
  
# Extras if time and asked to write, not that imp but better to know

from datetime import datetime

class Ticket:
    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time = None

    def close_ticket(self):
        self.exit_time = datetime.now()

    def get_duration_minutes(self):
        if not self.exit_time:
            return 0
        delta = self.exit_time - self.entry_time
        return max(1, delta.total_seconds() // 60)  # At least 1 minute charged


from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, ticket: Ticket) -> float:
        pass

class FlatRatePricing(PricingStrategy):
    def __init__(self, rate: float):
        self.rate = rate

    def calculate_price(self, ticket: Ticket) -> float:
        return self.rate

class DurationBasedPricing(PricingStrategy):
    def __init__(self, rate_per_minute: float):
        self.rate_per_minute = rate_per_minute

    def calculate_price(self, ticket: Ticket) -> float:
        duration = ticket.get_duration_minutes()
        return duration * self.rate_per_minute


class EntryGate:
    def __init__(self, parking_lot: ParkingLot):
        self.parking_lot = parking_lot

    def enter_vehicle(self, vehicle: Vehicle) -> Ticket:
        if self.parking_lot.park_vehicle(vehicle):
            # Simplified — assumes first level/spot handles ticket
            for level in self.parking_lot.levels:
                for spot in level.parking_spots:
                    if spot.get_parked_vehicle() == vehicle:
                        return Ticket(vehicle, spot)
        raise Exception("Parking failed or spot not found")

class ExitGate:
    def __init__(self, pricing_strategy: PricingStrategy):
        self.pricing_strategy = pricing_strategy

    def exit_vehicle(self, ticket: Ticket) -> float:
        ticket.close_ticket()
        fee = self.pricing_strategy.calculate_price(ticket)
        ticket.spot.unpark_vehicle()
        return fee

