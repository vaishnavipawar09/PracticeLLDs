# Clarifying Questions: Car Rental System
#How many cars and which makes/models do we support?  
#Are cars stationed at multiple rental locations, and can customers pick up/drop off at different sites?
#What rental durations do we allow (hourly, daily)?  
#Do we need to block a car for the entire requested period and prevent overlapping rentals?
#What’s the pricing model (flat daily rate, per-mile, late fees)?  
#Do we need deposits or credit holds?
#Can customers reserve in advance?  
#What’s our cancellation policy and refund rules?
# What customer info do we capture (ID, license, payment method)?  
#Do we track odometer start/end readings?
#How do we prevent double-booking when multiple agents/bookings occur in parallel?  
# Is in-memory OK or do we need persistent/transactional storage?
#Should we support upgrades (e.g., if requested car unavailable)?  
#Any loyalty/discount programs to plug in later?



# ✅ Verbal Design Pitch:
# We’re building a thread-safe Car Rental System that:
#  - Manages multiple Stores, each with Vehicles
#  - Lets Users search for available Vehicles by location & date range
#  - Handles Reservations (create & cancel), preventing any overlaps
#  - Calculates total cost = daily_rate × number of days
#  - Uses a Lock to ensure no double-booking under concurrent access

from __future__ import annotations
from datetime import date
from threading import Lock
from typing import List, Optional

#
# Core Classes:
# 1. Vehicle           — id, make, model, year, daily_rate, is_available flag
# 2. User              — id, name, contact
# 3. Store             — id, location, list of Vehicles with availability filter
# 4. Reservation       — id, User, Vehicle, start/end dates, total_cost
# 5. CarRentalSystem   — holds Users, Stores, Reservations; synchronizes bookings

class Vehicle:
    def __init__(self, vehicle_id: str, make: str, model: str, year: int, daily_rate: float):
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.year = year
        self.daily_rate = daily_rate
        self.is_available = True

class User:
    def __init__(self, user_id: int, name: str, contact: str):
        self.user_id = user_id
        self.name = name
        self.contact = contact

class Store:
    def __init__(self, store_id: int, location: str):
        self.store_id = store_id
        self.location = location
        self.vehicles: List[Vehicle] = []

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

    def get_available(self, start: date, end: date, reservations: List[Reservation]) -> List[Vehicle]:
        """Return vehicles free for the entire [start, end] window."""
        available = []
        for v in self.vehicles:
            if not v.is_available:
                continue
            # check overlap
            conflict = any(
                res.vehicle.vehicle_id == v.vehicle_id and
                not (end < res.start_date or start > res.end_date)
                for res in reservations
            )
            if not conflict:
                available.append(v)
        return available

class Reservation:
    def __init__(self, res_id: int, user: User, vehicle: Vehicle, start_date: date, end_date: date):
        self.reservation_id = res_id
        self.user = user
        self.vehicle = vehicle
        self.start_date = start_date
        self.end_date = end_date
        days = (end_date - start_date).days + 1
        self.total_cost = days * vehicle.daily_rate

class CarRentalSystem:
    """Main class managing users, stores, and reservations."""
    def __init__(self):
        self.users: List[User] = []
        self.stores: List[Store] = []
        self.reservations: List[Reservation] = []
        self._next_res_id = 1
        self._lock = Lock()

    def add_user(self, user: User):
        self.users.append(user)

    def add_store(self, store: Store):
        self.stores.append(store)

    def search_vehicles(self, location: str, start: date, end: date) -> List[Vehicle]:
        """Find all available vehicles at a given location and date range."""
        available: List[Vehicle] = []
        for store in self.stores:
            if store.location.lower() == location.lower():
                available.extend(store.get_available(start, end, self.reservations))
        return available

    def make_reservation(
        self, user: User, vehicle: Vehicle, start: date, end: date
    ) -> Optional[Reservation]:
        """Attempt to reserve; returns a Reservation or None if unavailable."""
        with self._lock:
            # double-check for overlap under lock
            for res in self.reservations:
                if res.vehicle.vehicle_id == vehicle.vehicle_id and not (end < res.start_date or start > res.end_date):
                    return None
            # book it
            vehicle.is_available = False
            res = Reservation(self._next_res_id, user, vehicle, start, end)
            self.reservations.append(res)
            self._next_res_id += 1
            return res

    def cancel_reservation(self, res_id: int) -> bool:
        """Cancel an existing reservation, freeing up the vehicle."""
        with self._lock:
            for i, res in enumerate(self.reservations):
                if res.reservation_id == res_id:
                    res.vehicle.is_available = True
                    self.reservations.pop(i)
                    return True
        return False

# --- Example Usage ---
if __name__ == "__main__":
    from datetime import date

    system = CarRentalSystem()

    # 1) Setup
    alice = User(1, "Alice", "alice@example.com")
    system.add_user(alice)
    downtown = Store(1, "Downtown")
    system.add_store(downtown)

    # 2) Add vehicles
    v1 = Vehicle("V001", "Toyota", "Corolla", 2022, 40)
    v2 = Vehicle("V002", "Honda",  "Civic",   2023, 45)
    downtown.add_vehicle(v1)
    downtown.add_vehicle(v2)

    # 3) Search & reserve
    start, end = date(2025,7,20), date(2025,7,22)
    available = system.search_vehicles("Downtown", start, end)
    print("Available:", [f"{v.make} {v.model}" for v in available])

    if available:
        res = system.make_reservation(alice, available[0], start, end)
        print("Reserved ID:", res.reservation_id, "Cost:", res.total_cost)

    # 4) Cancel reservation
    ok = system.cancel_reservation(res.reservation_id)
    print("Cancelled?", ok)
