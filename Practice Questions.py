#ParkingLot

#Vehicle: Car, Truck, Motorcycle
#Multiple levels and identical
#parking spot specifc type, and it has certain nuo. of slots
# how about payment ? is it a flat rate or duration rate? done at entry or exit ?  Duration rate

#vehicle(ABC)
#vehicletype
#parkingspot 
#level
#parkingLot
#Pricing 

from enum import Enum
class VehicleType(Enum):
    CAR = 1
    TRUCK = 2
    MOTORCYCLE = 3

from abc import ABC  
class Vehicle(ABC):
    def __init__(self, vehicle_type : VehicleType, license : str):
        self.vehicle_type = vehicle_type
        self.license = license
    
    def get_type(self) -> VehicleType:
        return self.get_type

class Car(Vehicle):
    def __init__(self, license: str):
        super().__init__(license, VehicleType.CAR)

class Truck(Vehicle):
    def __init__(self, license: str):
        super().__init__(license, VehicleType.TRUCK)

class MotorCycle(Vehicle):
    def __init__(self, license: str):
        super().__init__(license, VehicleType.MOTORCYCLE)
        
class ParkingSpot:
    def __init__(self, spot_number: int):
        self.spot_number = spot_number
        self.vehicle_type = VehicleType.Car
        self.park_vehicle = None
        
    def is_available(self) -> None:
        return self.park_vehicle is None
    
    def park_vehicle(self, vehicle: Vehicle) -> None:
        if self.is_available() and vehicle.get_type() == self.vehicle_type:
            self.park_vehicle = vehicle
        else:
            raise ValueError("Invalid")
        
    def unpark_vehicle(self) -> None:
        self.parked_vehicle = None
        
    def get_vehicle_type(self) -> VehicleType:
        return self.vehicle_type 
    
    def get_parked_vehicle(self) -> VehicleType:
        return self.vehicle_type 

from typing import List
        
class Level:
    def __init__(self, floor: int, num_spots: int):
        self.floor = floor
        self.parking_spots = List[ParkingSpot] = [ParkingSpot(i) for i in range(num_spots)]
        
    def park_vehicle(self, vehicle : Vehicle) -> bool:
        for spot in self.parking_spots:
            if spot.is_available() and spot.get_vehicle_type() == vehicle.get_type():
                spot.park_vehicle(vehicle)
                return True
        return False
    
    def unpark_vehicle(self, vehicle: Vehicle) -> bool:
        for spot in self.parking_spots:
            if not spot.is_available() and spot.get_parked_vehicle() == vehicle:
                spot.unpark_vehicle(vehicle)
                return True
        return False    
    
class ParkingLot:
    _instance = None
    
    def __init__(self):
        if ParkingLot._instance is not None:
            raise Exception("no")
        else:
            ParkingLot._instance = self
            self.levels : List[Level] = []
            
    @staticmethod
    def get_instance():
        if ParkingLot._instance is None:
            ParkingLot()
        return ParkingLot._instance
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        for level in self.levels:
            if level.park_vehicle(vehicle):
                return True
        return False
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        for level in self.levels:
            if level.unpark_vehicle(vehicle):
                return True
        return False
    
    
    
    
            
    
    
            
        
    