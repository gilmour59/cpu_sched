import os
import time
import collections

# --- Helper function to clear the terminal screen ---
def clear_screen():
    # 'nt' is for Windows, 'posix' is for macOS/Linux
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Process class remains the same ---
class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.start_time = -1
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.remaining_burst_time = burst_time

    def __repr__(self):
        return f"P{self.pid}"

# --- Schedulers are refactored as GENERATORS using 'yield' ---

def fcfs_scheduler(processes):
    """First-Come, First-Served Scheduling Generator"""
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    
    process_queue = collections.deque(processes)

    while len(completed) < len(processes):
        # Add newly arrived processes to the ready queue
        while process_queue and process_queue[0].arrival_time <= current_time:
            ready_queue.append(process_queue.popleft())
        
        if not running_process and ready_queue:
            running_process = ready_queue.pop(0)
        
        # Yield the current state BEFORE processing the time step
        yield current_time, running_process, ready_queue, completed

        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                running_process.completion_time = current_time + 1
                completed.append(running_process)
                running_process = None
        
        current_time += 1
        
    yield current_time, None, [], completed # Final state

def srtf_scheduler(processes):
    """Shortest Remaining Time First (SRTF) Scheduling Generator"""
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    
    remaining_procs = sorted(processes, key=lambda p: p.arrival_time)

    while len(completed) < len(processes):
        # Add newly arrived processes
        while remaining_procs and remaining_procs[0].arrival_time <= current_time:
            ready_queue.append(remaining_procs.pop(0))
        
        # Preemption check or select new process
        if ready_queue:
            ready_queue.sort(key=lambda p: p.remaining_burst_time)
            shortest_process = ready_queue[0]
            
            if running_process and shortest_process.remaining_burst_time < running_process.remaining_burst_time:
                # Preempt
                ready_queue.append(running_process)
                running_process = ready_queue.pop(0)
            elif not running_process:
                running_process = ready_queue.pop(0)

        # Yield the state to the visualizer
        yield current_time, running_process, ready_queue, completed

        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                running_process.completion_time = current_time + 1
                completed.append(running_process)
                running_process = None
                
        current_time += 1

    yield current_time, None, [], completed # Final state

# --- The Main Visual Simulator ---

class VisualSimulator:
    def __init__(self, processes, scheduler_func):
        self.processes = [Process(**p) for p in processes]
        self.scheduler = scheduler_func(self.processes)
        self.history = []

    def draw_state(self, time, running, ready, completed):
        clear_screen()
        print("--- CPU Scheduling Visualizer ---")
        print(f"Current Time: {time}")
        
        # CPU state
        cpu_state = f"[  {running}  ]" if running else "[ IDLE ]"
        print(f"CPU: {cpu_state}")
        
        # Ready Queue
        ready_state = ', '.join(map(str, ready)) if ready else "Empty"
        print(f"Ready Queue: [ {ready_state} ]")
        
        print("\n--- Processes ---")
        print("PID | Arrival | Burst | Remaining | Progress")
        print("----|---------|-------|-----------|--------------------")
        
        all_procs = sorted(self.processes, key=lambda p: p.pid)
        for p in all_procs:
            progress = (p.burst_time - p.remaining_burst_time) / p.burst_time
            bar_len = 15
            filled_len = int(bar_len * progress)
            progress_bar = '█' * filled_len + '-' * (bar_len - filled_len)
            
            status_line = f"{p.pid:<3} | {p.arrival_time:<7} | {p.burst_time:<5} | {p.remaining_burst_time:<9} | [{progress_bar}] {int(progress*100):>3}%"
            print(status_line)
            
        print("\n--- Completed ---")
        completed_pids = sorted([p.pid for p in completed])
        print(', '.join(map(str, completed_pids)) if completed else "None")
        print("-" * 35)

        # Store Gantt chart data
        if not self.history or self.history[-1] != cpu_state:
            self.history.append(cpu_state)

    def run(self, speed=0.5):
        try:
            # RENAMED the loop variable from 'time' to 'current_time'
            for current_time, running, ready, completed in self.scheduler:
                self.draw_state(current_time, running, ready, completed)
                # This now correctly calls the sleep method from the 'time' module
                time.sleep(speed)
        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")
        finally:
            print("\nSimulation Finished!")
            print("Gantt Chart (visual): " + " ".join(self.history))

if __name__ == "__main__":
    # Define your workload
    processes_data = [
        {'pid': 1, 'arrival_time': 0, 'burst_time': 7},
        {'pid': 2, 'arrival_time': 0, 'burst_time': 4},
        {'pid': 3, 'arrival_time': 4, 'burst_time': 1},
        {'pid': 4, 'arrival_time': 5, 'burst_time': 4},
    ]

    print("Select a scheduling algorithm to visualize:")
    print("1: First-Come, First-Served (FCFS)")
    print("2: Shortest Remaining Time First (SRTF)")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        scheduler_to_run = fcfs_scheduler
    elif choice == '2':
        scheduler_to_run = srtf_scheduler
    else:
        print("Invalid choice. Exiting.")
        exit()

    # The speed of the simulation (seconds per time step)
    simulation_speed = 0.4 
    
    simulator = VisualSimulator(processes_data, scheduler_to_run)
    simulator.run(speed=simulation_speed)