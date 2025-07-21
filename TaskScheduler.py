#clarifying Questions: Task Scheduler 

# Do we only need one-time delays, or must we support recurring schedules (e.g. “run every day at 9 AM” or “every N seconds”) 
# Will callers need to cancel or change a task after it’s scheduled? If so, should they do it by a returned handle or by task_id
# Do tasks need to survive a process restart (i.e. persist to disk/DB), or is purely in-memory scheduling acceptable?
# If task execution throws an error, should we retry automatically? How many times and with what interval?
# Roughly how many tasks per minute do we expect? Do we need multiple worker threads (a pool) or is a single thread acceptable?


#Verbal Pitch
# Task: Represents a self-contained unit of work that knows how to execute itself.
# ScheduledTask: Wraps a Task with its scheduled execution time., Enables comparison by timestamp so we can use a min-heap.
# TaskScheduler:
#   • Holds a min-heap of ScheduledTask objects.
#   • Runs a background thread that wakes up, checks the heap, and fires any tasks whose time has arrived.
#   • Provides schedule_task() and stop() APIs.

import time
import heapq
from datetime import datetime, timedelta
from threading import Thread, Lock

class Task:
    """A simple task to be executed."""
    def __init__(self, task_id, description):
        self.task_id = task_id
        self.description = description

    def execute(self):
        print(f"Executing Task {self.task_id}: {self.description} at {datetime.now()}")

class ScheduledTask:
    """A wrapper for a Task to include its execution time."""
    def __init__(self, task: Task, execute_at: datetime):
        self.task = task
        self.execute_at = execute_at

    # To make this class comparable for the min-heap
    def __lt__(self, other):
        return self.execute_at < other.execute_at           #heapq will use this to pop the earliest scheduled task first

class TaskScheduler:
    """A scheduler that executes tasks at their scheduled time."""
    def __init__(self):
        self.schedule = []           # Min-heap of ScheduledTask objects
        self._lock = Lock()          # Lock to guard access to the heap for thread safety
        self._running = True            # Flag to control the worker loop
        self.worker_thread = Thread(target=self._run)       # Start the background worker thread
        self.worker_thread.start()

    def schedule_task(self, task: Task, delay_seconds: int):
        """Schedules a task to run after a certain delay."""
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)      #excute at that particular time with delay
        scheduled_task = ScheduledTask(task, execute_at)            #call the scheduletask fucnt class 
        
        with self._lock:                                            #pushes the task to the heap
            heapq.heappush(self.schedule, scheduled_task)
            print(f"Scheduled Task {task.task_id} to run at {execute_at}")

    def _run(self):
        """The main loop that checks for and runs tasks."""
        while self._running:                                #start running the time at the date and time mentioned
            now = datetime.now()                            
            with self._lock:
                if self.schedule and self.schedule[0].execute_at <= now:        #• Under lock, checks if the heap’s earliest task is due.
                    task_to_run = heapq.heappop(self.schedule)          #If due, pops it and calls its execute() method.
                    task_to_run.task.execute()
            
            # Sleep for a short duration to avoid busy-waiting
            time.sleep(0.1)     #Repeatedly wakes up (every 0.1s) to avoid busy-waiting.

    def stop(self):
        """Stops the scheduler's worker thread."""
        self._running = False                   #  Signals the worker thread to exit and waits for it to finish.
        self.worker_thread.join()
        print("Task scheduler stopped.")
        
        
        
"""
Task – Self-contained work unit with an execute() method.

ScheduledTask – Wraps a Task with its execute_at timestamp and implements __lt__ so our min-heap can always pick the earliest job.

TaskScheduler –

Keeps a thread-safe min-heap (self.schedule) of ScheduledTask entries.

Spawns a background thread (_run) that:

Grabs the current time,

Under lock, peeks at the heap’s root,

If it’s due, heappop() and execute(),

Sleeps briefly to avoid busy-waiting.

Exposes schedule_task(...) (for one-off jobs) and stop() to shut down cleanly.

The min-heap gives us O(log n) inserts and removals and O(1) “peek” at the next task to run—perfect for an efficient scheduler."""

"""
This is with recurring task nad cancelation of the task code

import time
import heapq
from datetime import datetime, timedelta
from threading import Thread, Lock

class Task:
   
    def __init__(self, task_id, description):
        self.task_id = task_id
        self.description = description

    def execute(self):
        print(f"[{datetime.now()}] Executing Task {self.task_id}: {self.description}")

class ScheduledTask:
    
    def __init__(self, task: Task, execute_at: datetime, interval: int = None):
        self.task = task
        self.execute_at = execute_at
        self.interval = interval
        self.cancelled = False

    def __lt__(self, other):
        return self.execute_at < other.execute_at

class TaskScheduler:
    
    def __init__(self):
        self._lock = Lock()
        self._heap = []  # min-heap of ScheduledTask
        self._running = True
        self._worker = Thread(target=self._run, daemon=True)
        self._worker.start()

    def schedule_task(self, task: Task, delay_seconds: int) -> ScheduledTask:
       
        return self._schedule(task, delay_seconds, interval=None)

    def schedule_recurring(self, task: Task, delay_seconds: int, interval_seconds: int) -> ScheduledTask:
        
        return self._schedule(task, delay_seconds, interval=interval_seconds)

    def _schedule(self, task: Task, delay_seconds: int, interval: int = None) -> ScheduledTask:
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)
        handle = ScheduledTask(task, execute_at, interval)
        with self._lock:
            heapq.heappush(self._heap, handle)
        print(f"Scheduled {'recurring ' if interval else ''}task {task.task_id} at {execute_at}"
              f"{f' every {interval}s' if interval else ''}")
        return handle

    def cancel(self, handle: ScheduledTask) -> None:
       
        with self._lock:
            handle.cancelled = True
        print(f"Cancelled Task {handle.task.task_id}")

    def _run(self):
      
        while self._running:
            now = datetime.now()
            with self._lock:
                while self._heap and self._heap[0].execute_at <= now:
                    handle = heapq.heappop(self._heap)
                    if handle.cancelled:
                        continue
                    # execute outside lock to avoid blocking schedule/cancel
                    Thread(target=handle.task.execute).start()
                    # reschedule if recurring
                    if handle.interval is not None and not handle.cancelled:
                        handle.execute_at = now + timedelta(seconds=handle.interval)
                        heapq.heappush(self._heap, handle)
            time.sleep(0.1)

    def stop(self):
        
        self._running = False
        self._worker.join()
        print("Scheduler stopped.")
"""