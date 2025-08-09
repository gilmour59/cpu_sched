import collections

# A simple class to represent a process
class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        # These will be calculated during the simulation
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.start_time = -1
        self.remaining_burst_time = burst_time

    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival_time}, burst={self.burst_time})"

# --- SCHEDULER IMPLEMENTATIONS ---

class FCFSScheduler:
    def schedule(self, processes):
        """First-Come, First-Served Scheduling"""
        # Sort processes by arrival time to simulate the FCFS queue
        processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        gantt_chart = []
        
        for process in processes:
            # If the CPU is idle, fast-forward time to the process's arrival
            if current_time < process.arrival_time:
                gantt_chart.append(f"({current_time}-{process.arrival_time}: IDLE)")
                current_time = process.arrival_time
            
            process.start_time = current_time
            process.completion_time = current_time + process.burst_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            gantt_chart.append(f"({current_time}-{process.completion_time}: P{process.pid})")
            current_time = process.completion_time
            
        return processes, gantt_chart

class SJFScheduler:
    def schedule(self, processes):
        """Shortest Job First (Non-Preemptive) Scheduling"""
        current_time = 0
        completed_processes = []
        gantt_chart = []
        
        # Use a list of remaining processes, sorted by arrival to break ties
        remaining_processes = sorted(processes, key=lambda p: p.arrival_time)
        
        while remaining_processes:
            # Get all processes that have arrived and are ready to run
            ready_queue = [p for p in remaining_processes if p.arrival_time <= current_time]
            
            if not ready_queue:
                # If no process is ready, CPU is idle. Find the next arrival time.
                next_arrival_time = min(p.arrival_time for p in remaining_processes)
                gantt_chart.append(f"({current_time}-{next_arrival_time}: IDLE)")
                current_time = next_arrival_time
                continue

            # Sort the ready queue by burst time to find the shortest job
            ready_queue.sort(key=lambda p: p.burst_time)
            
            # Select the shortest job to execute
            process_to_run = ready_queue[0]
            
            process_to_run.start_time = current_time
            process_to_run.completion_time = current_time + process_to_run.burst_time
            process_to_run.turnaround_time = process_to_run.completion_time - process_to_run.arrival_time
            process_to_run.waiting_time = process_to_run.turnaround_time - process_to_run.burst_time
            
            gantt_chart.append(f"({current_time}-{process_to_run.completion_time}: P{process_to_run.pid})")
            current_time = process_to_run.completion_time
            
            completed_processes.append(process_to_run)
            remaining_processes.remove(process_to_run)
            
        return completed_processes, gantt_chart

class RoundRobinScheduler:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum

    def schedule(self, processes):
        """Round Robin Scheduling"""
        current_time = 0
        gantt_chart = []
        
        # Use a deque for an efficient ready queue (FIFO)
        ready_queue = collections.deque()
        
        # Sort processes by arrival time initially
        processes.sort(key=lambda p: p.arrival_time)
        process_idx = 0
        
        # List to store final completed processes
        completed_processes = []

        while process_idx < len(processes) or ready_queue:
            # Add newly arrived processes to the ready queue
            while process_idx < len(processes) and processes[process_idx].arrival_time <= current_time:
                ready_queue.append(processes[process_idx])
                process_idx += 1

            if not ready_queue:
                # If queue is empty, CPU is idle. Fast-forward to next process arrival.
                if process_idx < len(processes):
                    next_arrival_time = processes[process_idx].arrival_time
                    gantt_chart.append(f"({current_time}-{next_arrival_time}: IDLE)")
                    current_time = next_arrival_time
                continue

            # Get the next process from the front of the queue
            process = ready_queue.popleft()
            
            # Record start time on first run
            if process.start_time == -1:
                process.start_time = current_time
            
            # Determine execution time for this slice
            execution_time = min(process.remaining_burst_time, self.time_quantum)
            
            start_slice_time = current_time
            current_time += execution_time
            process.remaining_burst_time -= execution_time
            gantt_chart.append(f"({start_slice_time}-{current_time}: P{process.pid})")
            
            # Add any processes that arrived during this time slice
            while process_idx < len(processes) and processes[process_idx].arrival_time <= current_time:
                ready_queue.append(processes[process_idx])
                process_idx += 1

            if process.remaining_burst_time > 0:
                # If process is not finished, add it to the back of the queue
                ready_queue.append(process)
            else:
                # If process is finished, calculate its metrics
                process.completion_time = current_time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed_processes.append(process)
        
        # Sort by PID for consistent output
        completed_processes.sort(key=lambda p: p.pid)
        return completed_processes, gantt_chart


# --- SIMULATION AND REPORTING ---

def print_results(scheduler_name, completed_processes, gantt_chart):
    """Prints a formatted report of the simulation results."""
    print(f"--- {scheduler_name} ---")
    print("Gantt Chart: " + " ".join(gantt_chart))
    
    total_turnaround_time = 0
    total_waiting_time = 0
    
    print("PID | Arrival | Burst | Completion | Turnaround | Waiting")
    print("----|---------|-------|------------|------------|---------")
    for p in completed_processes:
        print(f"{p.pid:<3} | {p.arrival_time:<7} | {p.burst_time:<5} | {p.completion_time:<10} | {p.turnaround_time:<10} | {p.waiting_time:<7}")
        total_turnaround_time += p.turnaround_time
        total_waiting_time += p.waiting_time
        
    avg_turnaround_time = total_turnaround_time / len(completed_processes)
    avg_waiting_time = total_waiting_time / len(completed_processes)
    
    print(f"\nAverage Turnaround Time: {avg_turnaround_time:.2f}")
    print(f"Average Waiting Time: {avg_waiting_time:.2f}\n")


if __name__ == "__main__":
    # --- Define Your Workload ---
    # Workload 1: Mixed processes (from our previous example)
    #processes_data = [
    #    {'pid': 1, 'arrival_time': 0, 'burst_time': 7},
    #    {'pid': 2, 'arrival_time': 2, 'burst_time': 4},
    #    {'pid': 3, 'arrival_time': 4, 'burst_time': 1},
    #    {'pid': 4, 'arrival_time': 5, 'burst_time': 4},
    #]

    # You can define other workloads to test
    # Workload 2: All arrive at once (tests raw scheduling power)
    processes_data = [
        {'pid': 1, 'arrival_time': 0, 'burst_time': 8},
        {'pid': 2, 'arrival_time': 0, 'burst_time': 4},
        {'pid': 3, 'arrival_time': 0, 'burst_time': 5},
    ]

    # --- Run Simulations ---
    
    # FCFS Simulation
    fcfs_processes = [Process(**pd) for pd in processes_data]
    fcfs_scheduler = FCFSScheduler()
    fcfs_results, fcfs_gantt = fcfs_scheduler.schedule(fcfs_processes)
    print_results("First-Come, First-Served (FCFS)", fcfs_results, fcfs_gantt)
    
    # SJF Simulation
    sjf_processes = [Process(**pd) for pd in processes_data]
    sjf_scheduler = SJFScheduler()
    sjf_results, sjf_gantt = sjf_scheduler.schedule(sjf_processes)
    print_results("Shortest Job First (SJF)", sjf_results, sjf_gantt)
    
    # Round Robin Simulation
    rr_processes = [Process(**pd) for pd in processes_data]
    rr_scheduler = RoundRobinScheduler(time_quantum=3) # Let's use a time quantum of 3
    rr_results, rr_gantt = rr_scheduler.schedule(rr_processes)
    print_results("Round Robin (RR, Quantum=3)", rr_results, rr_gantt)