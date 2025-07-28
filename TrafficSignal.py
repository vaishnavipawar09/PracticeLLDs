#Clarifying Questions:

#should be able to control the traffic at an intersection with mulltiple road
#Different types of signal = red, yellow, green
#each light will have own configuration? yes
#Should each TrafficLight keep track of its current signal and update over time? yes
# Do we need a method to manually force a signal (for emergencies)? yes
#Does each road control its own light, or is that centralized? centralized - singleton pattern
# Should roads get green one at a time in a round-robin fashion? yes


# ✅ Verbal Design Pitch: Traffic Signal System
# We are designing a traffic light control system for a multi-road intersection.
# The system should:
# - Cycle between Red, Yellow, Green signals for each road
# - Use configurable durations for each signal
# - Handle emergency vehicles (e.g., ambulance/fire truck) with priority switching
# - Ensure only one road has Green at a time (others must be Red)
# - Be extensible to support real-time updates or sensors
#
# We'll implement the following components:
# 1. Signal (Enum) — Represents RED, YELLOW, GREEN
# 2. Road — Represents a road with an assigned traffic light
# 3. TrafficLight — Contains signal state, durations, and transition logic
# 4. TrafficController (Singleton) — Manages roads, timing, transitions, and emergencies
#
# We'll simulate time delays using `time.sleep()` in Python for transitions.

from enum import Enum

class Signal(Enum):
    RED = 1
    YELLOW = 2
    GREEN = 3
    
class Road:
    def __init__(self, road_id, name):
        self.name = name
        self.id = road_id
        self.traffic_light = None
    
    def set_traffic_light(self, traffic_light):
        self.traffic_light = traffic_light
        
    def get_traffic_light(self):
        return self.traffic_light
    
    def get_id(self):
        return self.id
    
from threading import Lock
class TrafficLight:
    def __init__(self, id: str, red_duration : int, green_duration: int, yellow_duration : int):
        self.id = id
        self.current_signal = Signal.RED
        self.red_duration = red_duration
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.lock = Lock()
        
    def change_signal(self, new_signal: Signal):
        with self.lock:
            self.current_signal = new_signal
    
    def get_current_signal(self):
        return self.current_signal
    
    
import threading   
import time

class TrafficController:
    _instance = None                    #holds the single shared instance.
    _lock = threading.Lock()            #ensures thread safety while creating that instance.
    
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.roads = {}            #dict of roads
        return cls._instance
    """Thread safety: multiple threads could call TrafficController() at the same time.

Double-checked locking: we first check if _instance is None outside the lock (fast path), then acquire the lock and check again before creating the instance.

Lock purpose: prevents two threads from both observing _instance as None and each creating a separate controller
""" 
    
    @classmethod
    def get_instance(cls):              #Public method to get the Singleton instance of TrafficController.
        return cls()
    
    def add_road(self, road: Road):     #Adds a Road object to the controller using its unique road.id.
        self.roads[road.id] = road

    def remove_road(self, road_id: str):    #Removes a road if it exists in the dictionary.
        self.roads.pop(road_id, None)
    
    def start_traffic_control(self):
        for road in self.roads.values():
            traffic_light = road.get_traffic_light()
            threading.Thread(target=self._control_traffic_light, args=(traffic_light,), daemon=True).start()        #Threads let the main thread stay responsive.
        #Starts a background thread to simulate that light's cycle.
        #daemon=True ensures threads shut down with the main program.
                
    def _control_traffic_light(self, traffic_light: TrafficLight):
        while True:
            try:
                time.sleep(traffic_light.red_duration / 1000)  # Convert to seconds
                traffic_light.change_signal(Signal.GREEN)
                time.sleep(traffic_light.green_duration / 1000)
                traffic_light.change_signal(Signal.YELLOW)
                time.sleep(traffic_light.yellow_duration / 1000)
                traffic_light.change_signal(Signal.RED)
            except Exception as e:
                print(f"Error in traffic light control: {e}")

    def handle_emergency(self, road_id: str):
        road = self.roads.get(road_id)
        if road:
            traffic_light = road.get_traffic_light()
            traffic_light.change_signal(Signal.GREEN)
            

def main():
    """
    Sets up a 4-way intersection with one road per direction,
    starts the traffic control loop, and simulates an emergency.
    """
    # Create controller (singleton)
    controller = TrafficController.get_instance()

    # Create roads and their lights
    north = Road("N", "North Road")
    north.set_traffic_light(TrafficLight("TL-N", red_duration=5000, green_duration=3000, yellow_duration=1000))
    east  = Road("E", "East Road")
    east.set_traffic_light(TrafficLight("TL-E", red_duration=5000, green_duration=3000, yellow_duration=1000))
    south = Road("S", "South Road")
    south.set_traffic_light(TrafficLight("TL-S", red_duration=5000, green_duration=3000, yellow_duration=1000))
    west  = Road("W", "West Road")
    west.set_traffic_light(TrafficLight("TL-W", red_duration=5000, green_duration=3000, yellow_duration=1000))

    # Register roads with the controller
    for road in (north, east, south, west):
        controller.add_road(road)

    # Start the background threads that cycle the lights
    controller.start_traffic_control()

    # Let it run for a bit...
    time.sleep(12)

    # Simulate an emergency on the East Road
    print("\n>>> Emergency detected on East Road! Forcing GREEN...\n")
    controller.handle_emergency("E")

    # Keep running so we can observe the effect
    time.sleep(5)

if __name__ == "__main__":
    main()
    
    
    """Independent Cycles
Each road’s light needs to cycle Red→Green→Yellow on its own schedule. By spinning up one thread per TrafficLight in start_traffic_control(), each light can sleep and wake on its own timing loop.

Non-blocking Main Flow
If you tried to drive all lights in a single loop, you’d either have to interleave their sleeps (ugly) or block the main thread (so you couldn’t handle things like emergencies or add/remove roads dynamically). Threads let the main thread stay responsive.

Simplicity of Simulation
Real traffic controllers are independent hardware units. Threads give us a simple way to mimic that—each thread just runs:

while True:
  sleep(red)
  change(GREEN)
  sleep(green)
  change(YELLOW)
  sleep(yellow)
  change(RED)
Meanwhile, your main program can still respond to events (e.g. handle_emergency) immediately.

Scalability & Extensibility
Down the road you might add sensors or dynamic timing adjustments. With a threaded model, each light can listen for sensor updates, adjust its own timers, or be paused/stopped without rewriting a monolithic event loop.

In short, threads let us model each traffic‐light’s autonomous behavior and keep the system reactive to external events (like emergencies) in a very natural, decoupled way.
    """