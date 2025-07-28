#  Clarifying Questions

# 🛗 Clarifying Questions: Elevator Control System
# 1. Building Layout:
#    – How many floors (N) and how many elevator cars (M) are we modeling?
# 2. Capacity & Constraints:
#    – What is the maximum passenger capacity per car?
#    – Should we model weight limits or just rider counts?
# 3. Request Types:
#    – Do we need both external (hall) calls and internal (car-panel) requests?
#    – Can passengers cancel a request before pickup?
# 4. Scheduling Policy:
#    – Which dispatch strategy? (e.g., nearest-car first, lookup table, collective control)
#    – Should idle cars return to a “home” floor when unused?
# 5. Concurrency & Safety:
#    – Must multiple threads handle simultaneous button presses and car movements?
#    – Any emergency mode (fire service, priority override)?
# 6. Door & Timing:
#    – How long do doors stay open? Do we need explicit door-open/close events?
# 7. Fault Handling:
#    – Do we need to handle an out-of-service car?
# 8. Extensibility:
#    – Future features: express elevators, VIP mode, load balancing?

# ✅ Verbal Design Pitch: Elevator Control System
# We are building a control system for M elevator cars serving N floors.
# Core responsibilities:
# - Model each Elevator car’s state (current floor, direction, queued requests)
# - Accept hall-calls (source_floor → destination_floor) and dispatch the “best” car
# - Process each car’s internal queue in FIFO order, simulating movement and door stops
# - Ensure thread‐safe request enqueueing and worker threads per car
#
# Key Classes & Methods:
# 1. Direction (Enum)
#    • UP or DOWN to indicate travel direction
#
# 2. Request
#    • source_floor, destination_floor
#    • Encapsulates a pickup + drop-off in one object
#
# 3. Elevator
#    • id, capacity (max concurrent requests), current_floor, current_direction
#    • requests: List[Request] – a FIFO queue of pending rides
#    • lock, condition: synchronize add_request and get_next_request
#    • add_request(request): under lock, enqueue if capacity allows, then notify worker
#    • get_next_request() → blocks until a request is available
#    • process_requests(): loop forever, pop each request and call process_request()
#    • process_request(req): step floor by floor toward destination, update current_floor and direction, simulate travel
#    • run(): entrypoint for the worker thread → calls process_requests()
#
# 4. ElevatorController
#    • elevators: List[Elevator]
#    • On init, spins up one thread per Elevator.run()
#    • request_elevator(src, dst): picks optimal car (smallest |src - current_floor|) and add_request()
#    • find_optimal_elevator(src, dst): simple nearest-car dispatch strategy
#
# Thread Safety:
# - Each Elevator has its own lock+condition so multiple cars can run in parallel
# - Controller only reads elevator.current_floor under no lock; in real system, would need synchronization
#
# Extensions (not shown):
# - Support cancellation of requests
# - Use separate up/down queues and priority scheduling (SCAN algorithm)
# - Handle “stop at intermediate floors” for multi-passenger rides
# - Emergency override, door-open timing, fault detection

from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    
class Request:
    def __init__(self, source_floor, destination_floor):
        self.source_floor = source_floor
        self.destination_floor = destination_floor
        
import time
from threading import Lock, Condition
class Elevator:
    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity
        self.current_floor = 1
        self.current_direction = Direction.UP
        self.requests = []          ## FIFO queue of pending Request objects
        self.lock = Lock()          # Guards access to requests
        self.condition = Condition(self.lock)
        
    def add_request(self, request: Request):
        """Thread-safe enqueue of a new ride request, up to capacity."""
        with self.lock:
            if len(self.requests) < self.capacity:
                self.requests.append(request)
                print(f"[Elevator {self.id}] added request: {request.source_floor} → {request.destination_floor}")
                self.condition.notify()     # Wake up processing thread if waiting

    def get_next_request(self) -> Request:
        """Block until at least one request is available, then dequeue."""
        with self.condition:
            while not self.requests:
                self.condition.wait()
            return self.requests.pop(0)
        
    def process_requests(self):
        """Continuously fetch and execute ride requests."""
        while True:
            req = self.get_next_request()
            self.process_request(req)

    def process_request(self, request: Request):
        """Move to the destination floor step-by-step, updating state."""
        start = self.current_floor
        end = request.destination_floor

        # Determine travel direction
        if start < end:
            self.current_direction = Direction.UP
            step = 1
        else:
            self.current_direction = Direction.DOWN
            step = -1

        # Simulate movement one floor at a time
        for floor in range(start, end + step, step):
            self.current_floor = floor
            print(f"[Elevator {self.id}] at floor {self.current_floor}")
            time.sleep(1)

    def run(self):
        """Thread entrypoint to start processing."""
        self.process_requests()
        
from threading import Thread
class ElevatorController:
    def __init__(self, num_elevators: int, capacity: int):
        self.elevators = []
        # Initialize and start one worker thread per elevator
        for i in range(num_elevators):
            elevator = Elevator(i + 1, capacity)
            self.elevators.append(elevator)
            Thread(target=elevator.run).start()

    def request_elevator(self, source_floor: int, destination_floor: int):
        """Assign the nearest elevator to the new request."""
        best = self.find_optimal_elevator(source_floor, destination_floor)
        best.add_request(Request(source_floor, destination_floor))

    def find_optimal_elevator(self, source_floor: int, destination_floor: int) -> Elevator:
        """Nearest‐car dispatch: pick elevator with minimal |current_floor – source_floor|."""
        best = None
        min_dist = float('inf')
        for elevator in self.elevators:
            dist = abs(source_floor - elevator.current_floor)
            if dist < min_dist:
                min_dist = dist
                best = elevator
        return best
    
if __name__ == "__main__":
    import time

    # Create a controller with 3 elevators, each can queue up to 5 requests
    controller = ElevatorController(num_elevators=3, capacity=5)

    # Simulate a few hall calls
    controller.request_elevator(source_floor=1, destination_floor=7)
    controller.request_elevator(source_floor=3, destination_floor=10)
    controller.request_elevator(source_floor=5, destination_floor=2)

    # Let the simulation run for a bit so you can see the elevators moving
    time.sleep(15)

        
"""
controller = ElevatorController(num_elevators=2, capacity=2)
# Elevators start at floor 1, idle

# 1) First request: from floor 1 → floor 5
controller.request_elevator(1, 5)
# └─ find_optimal_elevator scans both cars:
#     • Car A (floor 1) → distance=0
#     • Car B (floor 1) → distance=0
#   it picks Car A (first min), and enqueues Request(1→5) into Car A’s queue.
#   Car A’s worker thread wakes up, pops request, and starts moving:
#     prints: [Elevator 1] at floor 1,2,3,4,5

# 2) Shortly after, second request: from floor 3 → floor 2
controller.request_elevator(3, 2)
# └─ find_optimal_elevator again:
#     • Car A is now at floor 5 → dist=|3–5|=2
#     • Car B is still at floor 1 → dist=|3–1|=2
#   ties go to Car A again; it enqueues Request(3→2) (capacity = 2, so OK).
#   Car A will finish its first trip, then process the second:
#     prints: [Elevator 1] at floor 4,3,2

Meanwhile Car B’s queue is empty and remains idle.



Whenever you need to always pull out the “smallest” (earliest) element, a min-heap is the right choice:

O(1) peek of the next execution time: heap[0] is always the smallest timestamp.

O(log n) insertion/removal: pushing a new task or popping the next‐due one costs logarithmic time—much better than a sorted list (O(n) inserts) or rescanning an unsorted list (O(n) finds).

In contrast, for the per-elevator FIFO queue we used a simple Python list (appending is amortized O(1)),
because each elevator’s capacity is small and bounded—so the occasional O(n) pop-from-front is acceptable. 
In a high-scale system you’d swap that for collections.deque to get true O(1) pops on both ends.

        """