import os
import time
import collections
import random # Needed for Lottery Scheduling

# --- Helper function to clear the terminal screen ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Process class is updated with a 'tickets' attribute ---
class Process:
    def __init__(self, pid, arrival_time, burst_time, tickets=10): # tickets added
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.tickets = tickets # For lottery scheduling
        
        # Simulation state attributes
        self.start_time = -1
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.remaining_burst_time = burst_time

    def __repr__(self):
        # A simple representation for clean printing in queues
        return f"P{self.pid}"

# --- SCHEDULER GENERATORS ---

def fcfs_scheduler(processes):
    # This function remains the same as before
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
    # This function remains the same as before
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
    """Round Robin Scheduling Generator"""
    current_time = 0
    ready_queue = collections.deque() # Use a deque for efficient FIFO queue
    completed = []
    running_process = None
    quantum_slice = 0 # To track time slice usage
    
    procs_to_arrive = sorted(processes, key=lambda p: p.arrival_time)

    while len(completed) < len(processes):
        # Add newly arrived processes to the back of the ready queue
        while procs_to_arrive and procs_to_arrive[0].arrival_time <= current_time:
            ready_queue.append(procs_to_arrive.pop(0))

        if not running_process and ready_queue:
            running_process = ready_queue.popleft()
            quantum_slice = 0 # Reset quantum for new process

        yield current_time, running_process, list(ready_queue), completed

        if running_process:
            running_process.remaining_burst_time -= 1
            quantum_slice += 1
            
            if running_process.remaining_burst_time == 0:
                completed.append(running_process)
                running_process = None
            elif quantum_slice == time_quantum:
                # Time quantum expired, preempt and move to back of queue
                ready_queue.append(running_process)
                running_process = None
        
        current_time += 1
    yield current_time, None, [], completed


def lottery_scheduler(processes):
    """Lottery Scheduling Generator (Non-Preemptive)"""
    current_time = 0
    ready_queue = []
    completed = []
    running_process = None
    
    procs_to_arrive = sorted(processes, key=lambda p: p.arrival_time)
    
    while len(completed) < len(processes):
        while procs_to_arrive and procs_to_arrive[0].arrival_time <= current_time:
            ready_queue.append(procs_to_arrive.pop(0))

        if not running_process and ready_queue:
            # --- The Lottery Draw ---
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


# --- Main Visual Simulator (no changes needed) ---
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
        print("PID | Arrival | Burst | Rem | Tickets | Progress")
        print("----|---------|-------|-----|---------|--------------------")
        
        all_procs = sorted(self.processes, key=lambda p: p.pid)
        for p in all_procs:
            progress = (p.burst_time - p.remaining_burst_time) / p.burst_time
            bar_len = 15
            filled_len = int(bar_len * progress)
            progress_bar = '█' * filled_len + '-' * (bar_len - filled_len)
            print(f"{p.pid:<3} | {p.arrival_time:<7} | {p.burst_time:<5} | {p.remaining_burst_time:<3} | {p.tickets:<7} | [{progress_bar}] {int(progress*100):>3}%")
            
        print("\n--- Completed ---")
        completed_pids = sorted([p.pid for p in completed])
        print(', '.join(map(str, completed_pids)) if completed else "None")
        print("-" * 45)

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


# --- Main execution block with updated menu ---
if __name__ == "__main__":
    processes_data = [
        {'pid': 1, 'arrival_time': 0, 'burst_time': 8, 'tickets': 30},
        {'pid': 2, 'arrival_time': 0, 'burst_time': 10, 'tickets': 30},
        {'pid': 3, 'arrival_time': 4, 'burst_time': 2, 'tickets': 5},
        {'pid': 4, 'arrival_time': 5, 'burst_time': 5, 'tickets': 10},
    ]

    print("Select a scheduling algorithm to visualize:")
    print("1: First-Come, First-Served (FCFS)")
    print("2: Shortest Remaining Time First (SRTF)")
    print("3: Round Robin (RR)")
    print("4: Lottery Scheduling")
    choice = input("Enter your choice (1-4): ")

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
    else:
        print("Invalid choice. Exiting.")

    if scheduler_to_run:
        simulation_speed = 0.4
        simulator = VisualSimulator(processes_data, scheduler_to_run)
        simulator.run(speed=simulation_speed)