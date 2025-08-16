import os
import time
import collections
import random

# --- Helper function to clear the terminal screen ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Process class is updated with a 'deadline' attribute ---
class Process:
    def __init__(self, pid, arrival_time, burst_time, tickets=10, deadline=0): # deadline added
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.tickets = tickets
        self.deadline = deadline # For EDF scheduling
        
        # Simulation state attributes
        self.start_time = -1
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.remaining_burst_time = burst_time

    def __repr__(self):
        return f"P{self.pid}"

# --- SCHEDULER GENERATORS ---
# FCFS, SRTF, Round Robin, and Lottery schedulers remain the same.
# For brevity, they are omitted here but are required in the final script.
# You can copy them from the previous response.

def fcfs_scheduler(processes):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    process_queue = collections.deque(processes)
    while len(completed) < len(processes):
        while process_queue and process_queue[0].arrival_time <= current_time:
            ready_queue.append(process_queue.popleft())
        if not running_process and ready_queue:
            running_process = ready_queue.pop(0)
        yield current_time, running_process, ready_queue, completed
        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
        current_time += 1
    yield current_time, None, [], completed

def srtf_scheduler(processes):
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    remaining_procs = sorted(processes, key=lambda p: p.arrival_time)
    while len(completed) < len(processes):
        while remaining_procs and remaining_procs[0].arrival_time <= current_time:
            ready_queue.append(remaining_procs.pop(0))
        if ready_queue:
            ready_queue.sort(key=lambda p: p.remaining_burst_time)
            shortest_process = ready_queue[0]
            if running_process and shortest_process.remaining_burst_time < running_process.remaining_burst_time:
                ready_queue.append(running_process)
                running_process = ready_queue.pop(0)
            elif not running_process:
                running_process = ready_queue.pop(0)
        yield current_time, running_process, ready_queue, completed
        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
        current_time += 1
    yield current_time, None, [], completed

def round_robin_scheduler(processes, time_quantum):
    current_time = 0
    ready_queue = collections.deque()
    completed = []
    running_process = None
    quantum_slice = 0
    procs_to_arrive = sorted(processes, key=lambda p: p.arrival_time)
    while len(completed) < len(processes):
        while procs_to_arrive and procs_to_arrive[0].arrival_time <= current_time:
            ready_queue.append(procs_to_arrive.pop(0))
        if not running_process and ready_queue:
            running_process = ready_queue.popleft()
            quantum_slice = 0
        yield current_time, running_process, list(ready_queue), completed
        if running_process:
            running_process.remaining_burst_time -= 1
            quantum_slice += 1
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
            elif quantum_slice == time_quantum:
                ready_queue.append(running_process)
                running_process = None
        current_time += 1
    yield current_time, None, [], completed

def lottery_scheduler(processes):
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    procs_to_arrive = sorted(processes, key=lambda p: p.arrival_time)
    while len(completed) < len(processes):
        while procs_to_arrive and procs_to_arrive[0].arrival_time <= current_time:
            ready_queue.append(procs_to_arrive.pop(0))
        if not running_process and ready_queue:
            total_tickets = sum(p.tickets for p in ready_queue)
            if total_tickets > 0:
                winning_ticket = random.randint(1, total_tickets)
                ticket_sum = 0
                for process in ready_queue:
                    ticket_sum += process.tickets
                    if ticket_sum >= winning_ticket:
                        running_process = process
                        break
                ready_queue.remove(running_process)
        yield current_time, running_process, ready_queue, completed
        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
        current_time += 1
    yield current_time, None, [], completed

def edf_scheduler(processes):
    """Earliest Deadline First (EDF) Scheduling Generator"""
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    procs_to_arrive = sorted(processes, key=lambda p: p.arrival_time)
    
    while len(completed) < len(processes):
        # Add newly arrived processes to the ready queue
        while procs_to_arrive and procs_to_arrive[0].arrival_time <= current_time:
            ready_queue.append(procs_to_arrive.pop(0))

        if ready_queue:
            # Sort the ready queue by the earliest deadline
            ready_queue.sort(key=lambda p: p.deadline)
            earliest_deadline_proc = ready_queue[0]
            
            # Preemption Check: if a new process has an earlier deadline
            if running_process and earliest_deadline_proc.deadline < running_process.deadline:
                ready_queue.append(running_process)
                running_process = ready_queue.pop(0)
            elif not running_process:
                running_process = ready_queue.pop(0)
        
        yield current_time, running_process, ready_queue, completed

        if running_process:
            running_process.remaining_burst_time -= 1
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
        
        current_time += 1
    yield current_time, None, [], completed

# --- Main Visual Simulator (updated draw_state) ---
class VisualSimulator:
    def __init__(self, processes, scheduler_func):
        self.processes = [Process(**p) for p in processes]
        self.scheduler = scheduler_func(self.processes)
        self.history = []

    def draw_state(self, current_time, running, ready, completed):
        clear_screen()
        print("--- CPU Scheduling Visualizer ---")
        print(f"Current Time: {current_time}")
        cpu_state = f"[  {running}  ]" if running else "[ IDLE ]"
        print(f"CPU: {cpu_state}")
        ready_state = ', '.join(map(str, ready)) if ready else "Empty"
        print(f"Ready Queue: [ {ready_state} ]")
        
        print("\n--- Processes ---")
        print("PID | Arrival | Burst | Rem | Deadline | Tickets | Progress")
        print("----|---------|-------|-----|----------|---------|--------------------")
        
        all_procs = sorted(self.processes, key=lambda p: p.pid)
        for p in all_procs:
            progress = (p.burst_time - p.remaining_burst_time) / p.burst_time
            bar_len = 15
            filled_len = int(bar_len * progress)
            progress_bar = '█' * filled_len + '-' * (bar_len - filled_len)
            print(f"{p.pid:<3} | {p.arrival_time:<7} | {p.burst_time:<5} | {p.remaining_burst_time:<3} | {p.deadline:<8} | {p.tickets:<7} | [{progress_bar}] {int(progress*100):>3}%")
            
        print("\n--- Completed ---")
        completed_pids = sorted([p.pid for p in completed])
        print(', '.join(map(str, completed_pids)) if completed else "None")
        print("-" * 55)

        if not self.history or self.history[-1] != cpu_state:
            self.history.append(cpu_state)

    def run(self, speed=0.5):
        try:
            for current_time, running, ready, completed in self.scheduler:
                self.draw_state(current_time, running, ready, completed)
                time.sleep(speed)
        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")
        finally:
            print("\nSimulation Finished!")
            print("Gantt Chart (visual): " + " ".join(self.history))


if __name__ == "__main__":
    processes_data = [ 
        {'pid': 1, 'arrival_time': 0, 'burst_time': 3, 'tickets': 10, 'deadline': 9},
        {'pid': 2, 'arrival_time': 2, 'burst_time': 5, 'tickets': 15, 'deadline': 16},
        {'pid': 3, 'arrival_time': 4, 'burst_time': 4, 'tickets': 20, 'deadline': 18},
        {'pid': 4, 'arrival_time': 5, 'burst_time': 2, 'tickets': 10, 'deadline': 20},
        {'pid': 5, 'arrival_time': 7, 'burst_time': 3, 'tickets': 25, 'deadline': 15},
        {'pid': 6, 'arrival_time': 9, 'burst_time': 4, 'tickets': 5,  'deadline': 25},
        {'pid': 7, 'arrival_time': 12, 'burst_time': 2, 'tickets': 15, 'deadline': 22},
    ]

    print("Select a scheduling algorithm to visualize:")
    print("1: First-Come, First-Served (FCFS)")
    print("2: Shortest Remaining Time First (SRTF)")
    print("3: Round Robin (RR)")
    print("4: Lottery Scheduling")
    print("5: Earliest Deadline First (EDF)")
    choice = input("Enter your choice (1-5): ")

    scheduler_to_run = None
    if choice == '1':
        scheduler_to_run = lambda procs: fcfs_scheduler(procs)
    elif choice == '2':
        scheduler_to_run = lambda procs: srtf_scheduler(procs)
    elif choice == '3':
        try:
            quantum = int(input("Enter Time Quantum for Round Robin: "))
            scheduler_to_run = lambda procs: round_robin_scheduler(procs, time_quantum=quantum)
        except ValueError:
            print("Invalid quantum. Exiting.")
    elif choice == '4':
        scheduler_to_run = lambda procs: lottery_scheduler(procs)
    elif choice == '5':
        scheduler_to_run = lambda procs: edf_scheduler(procs)
    else:
        print("Invalid choice. Exiting.")

    if scheduler_to_run:
        simulation_speed = 0.5
        simulator = VisualSimulator(processes_data, scheduler_to_run)
        simulator.run(speed=simulation_speed)