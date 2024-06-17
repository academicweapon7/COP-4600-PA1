import sys
# Component 1 
class Process:
    def __init__(self, name, arrival_time, burst_time):
        self.name = name
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.remaining_time = int(burst_time)
        self.status = 'waiting'  # can be 'waiting', 'running', or 'completed'
        self.start_time = -1
        self.finish_time = -1

    def __repr__(self):
        return f"{self.name}({self.arrival_time},{self.burst_time},{self.status})"


def read_processes(filename):
    processes = []
    with open(filename, 'r') as file:
        for line in file:
            name, arrival, burst = line.strip().split(',')
            processes.append(Process(name, arrival, burst))
    return processes


# Example usage:
process_list = read_processes('processes.txt')
print(process_list)
#End of Component 1
def fifo(runfor, processcount, processes):
    current_time = 0
    timeline = []  # To store events for output

    # Sort processes by arrival time (although FIFO doesn't strictly require sorting)
    processes.sort(key=lambda x: x[0])

    while current_time < runfor:
        for arrival, burst in processes:
            if arrival <= current_time:
                timeline.append(f"Time {current_time:3}: Process {chr(65 + len(timeline))} selected (burst {burst})")
                current_time += burst
                timeline.append(f"Time {current_time:3}: Process {chr(65 + len(timeline) - 1)} finished")

    print("\n".join(timeline))

def sjf(runfor, processcount, processes):
    current_time = 0
    timeline = []  # To store events for output
    processes = sorted(processes, key=lambda x: x[0])  # Sort processes by arrival time initially

    while current_time < runfor:
        ready_processes = [p for p in processes if p[0] <= current_time]

        if not ready_processes:
            timeline.append(f"Time {current_time:3}: Idle")
            current_time += 1
            continue

        shortest_job = min(ready_processes, key=lambda x: x[1])
        process_index = processes.index(shortest_job)

        timeline.append(f"Time {current_time:3}: Process {chr(65 + process_index)} selected (burst {shortest_job[1]})")
        current_time += shortest_job[1]
        timeline.append(f"Time {current_time:3}: Process {chr(65 + process_index)} finished")
        processes.pop(process_index)

    print("\n".join(timeline))

def rr(runfor, processcount, processes, quantum):
    current_time = 0
    timeline = []  # To store events for output
    queue = processes[:]  # Copy of processes as the queue

    while queue or current_time < runfor:
        if not queue:
            timeline.append(f"Time {current_time:3}: Idle")
            current_time += 1
            continue

        process = queue.pop(0)
        timeline.append(f"Time {current_time:3}: Process {chr(65 + len(timeline))} selected (burst {process[1]})")

        if process[1] <= quantum:
            current_time += process[1]
            timeline.append(f"Time {current_time:3}: Process {chr(65 + len(timeline) - 1)} finished")
        else:
            current_time += quantum
            process[1] -= quantum
            queue.append(process)
            timeline.append(f"Time {current_time:3}: Process {chr(65 + len(timeline) - 1)} preempted (remaining {process[1]})")

    print("\n".join(timeline))

def read_input_filename():
    # Check if the number of command-line arguments is correct
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_filename>")
        sys.exit(1)
    
    # Get the input filename from the command-line arguments
    input_filename = sys.argv[1]
    
    try:
        # Try to open the file
        with open(input_filename, 'r') as file:
            lines = file.readlines()
        
        # Initialize variables
        runfor = None
        processcount = None
        scheduler = None
        quantum = None
        processes = []
        
        # Parse the file content
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("processcount"):
                processcount = int(line.split()[1])
            elif line.startswith("runfor"):
                runfor = int(line.split()[1])
            elif line.startswith("use"):
                scheduler = line.split()[1]
                # If the scheduler is rr, read the next line for quantum
                if scheduler == "rr":
                    quantum_line = lines[i + 1].strip()
                    if quantum_line.startswith("quantum"):
                        quantum = int(quantum_line.split()[1])
                    else:
                        print("Error: Missing quantum parameter when use is 'rr'.")
                        sys.exit(1)
            elif line.startswith("process"):
                parts = line.split()
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append([arrival, burst])
            elif line.startswith("end"):
                break
        
        # Check if all required information is present
        if runfor is None:
            print("Error: Missing parameter runfor.")
            sys.exit(1)
        if processcount is None:
            print("Error: Missing parameter processcount.")
            sys.exit(1)
        if scheduler is None:
            print("Error: Missing parameter scheduler.")
            sys.exit(1)
        if len(processes) != processcount:
            print("Error: Incorrect number of processes.")
            sys.exit(1)
        
        # Call the appropriate scheduler function
        if scheduler == "fifo":
            fifo(runfor, processcount, processes)
        elif scheduler == "sjf":
            sjf(runfor, processcount, processes)
        elif scheduler == "rr":
            if quantum is None:
                print("Error: Missing quantum parameter when use is 'rr'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' does not exist.")
        sys.exit(1)
    except IOError as e:
        print(f"Error: An IOError occurred while trying to open the file '{input_filename}'.")
        print(e)
        sys.exit(1)

# Call the function to test it
if __name__ == "__main__":
    read_input_filename()
