import sys

def fifo(runfor, processcount, processes):
    output_lines = []
    current_time = 0
    queue = []
    finished_processes = []
    in_queue = set()
    process_stats = {process_id: {'wait': 0, 'turnaround': 0, 'response': -1} for _, _, process_id in processes}

    processes = sorted(processes, key=lambda x: x[0])  # Sort processes by arrival time

    output_lines.append(f"  {processcount} processes")
    output_lines.append("Using First In First Out")

    while current_time < runfor:
        for arrival, burst, process_id in processes:
            if arrival == current_time and process_id not in in_queue:
                queue.append((arrival, burst, process_id))
                in_queue.add(process_id)
                output_lines.append(f"Time {current_time:3} : Process {process_id} arrived")

        if queue:
            arrival, burst, process_id = queue.pop(0)
            in_queue.remove(process_id)
            if process_stats[process_id]['response'] == -1:
                process_stats[process_id]['response'] = current_time - arrival
            output_lines.append(f"Time {current_time:3} : Process {process_id} selected (burst {burst:3})")
            for t in range(burst):
                current_time += 1
                for arr, brst, proc_id in processes:
                    if arr == current_time and proc_id not in in_queue:
                        queue.append((arr, brst, proc_id))
                        in_queue.add(proc_id)
                        output_lines.append(f"Time {current_time:3} : Process {proc_id} arrived")
                if current_time >= runfor:
                    break
            finished_processes.append((arrival, burst, process_id))
            process_stats[process_id]['turnaround'] = current_time - arrival
            process_stats[process_id]['wait'] = process_stats[process_id]['turnaround'] - burst
            output_lines.append(f"Time {current_time:3} : Process {process_id} finished")
        else:
            output_lines.append(f"Time {current_time:3} : Idle")
            current_time += 1

    output_lines.append(f"Finished at time {runfor}")
    output_lines.append("")

    for process_id in sorted(process_stats.keys()):
        wait = process_stats[process_id]['wait']
        turnaround = process_stats[process_id]['turnaround']
        response = process_stats[process_id]['response']
        output_lines.append(f"Process {process_id} wait {wait:3} turnaround {turnaround:3} response {response:3}")

    # Write the output to a file
    with open('output.out', 'w') as file:
        for line in output_lines:
            file.write(line + '\n')

def sjf(runfor, processcount, processes):
    print(f"Called SJF with runfor={runfor}, processcount={processcount}, processes={processes}")

def rr(runfor, processcount, processes, quantum):
    output_lines = []
    current_time = 0
    queue = []
    in_queue = set()
    process_stats = {process_id: {'wait': 0, 'turnaround': 0, 'response': -1, 'remaining_burst': burst} for arrival, burst, process_id in processes}

    processes = sorted(processes, key=lambda x: x[0])  # Sort processes by arrival time

    output_lines.append(f"  {processcount} processes")
    output_lines.append("Using Round-Robin")
    output_lines.append(f"Quantum   {quantum}")
    output_lines.append("")

    wait_times = {process_id: 0 for _, _, process_id in processes}
    last_seen = {process_id: -1 for _, _, process_id in processes}

    while current_time < runfor:
        # Add newly arrived processes to the queue
        for arrival, burst, process_id in processes:
            if arrival == current_time and process_id not in in_queue:
                queue.append(process_id)
                in_queue.add(process_id)
                output_lines.append(f"Time {current_time:3} : {process_id} arrived")

        if queue:
            process_id = queue.pop(0)
            in_queue.remove(process_id)
            arrival, burst = [(arr, brst) for arr, brst, pid in processes if pid == process_id][0]
            remaining_burst = process_stats[process_id]['remaining_burst']

            if process_stats[process_id]['response'] == -1:
                process_stats[process_id]['response'] = current_time - arrival

            if last_seen[process_id] != -1:
                wait_times[process_id] += (current_time - last_seen[process_id])

            run_time = min(quantum, remaining_burst)
            output_lines.append(f"Time {current_time:3} : {process_id} selected (burst {remaining_burst:3})")

            for _ in range(run_time):
                current_time += 1
                remaining_burst -= 1
                # Add newly arrived processes during the execution
                for arr, brst, pid in processes:
                    if arr == current_time and pid not in in_queue:
                        queue.append(pid)
                        in_queue.add(pid)
                        output_lines.append(f"Time {current_time:3} : {pid} arrived")
                if current_time >= runfor:
                    break

            process_stats[process_id]['remaining_burst'] = remaining_burst

            if remaining_burst > 0:
                queue.append(process_id)
                in_queue.add(process_id)
                last_seen[process_id] = current_time
            else:
                process_stats[process_id]['turnaround'] = current_time - arrival
                output_lines.append(f"Time {current_time:3} : {process_id} finished")
                last_seen[process_id] = -1
        else:
            output_lines.append(f"Time {current_time:3} : Idle")
            current_time += 1

    output_lines.append(f"Finished at time {runfor}")
    output_lines.append("")

    for process_id in sorted(process_stats.keys()):
        turnaround = process_stats[process_id]['turnaround']
        response = process_stats[process_id]['response']
        wait = wait_times[process_id]
        output_lines.append(f"{process_id} wait {wait:3} turnaround {turnaround:3} response {response:3}")

    # Write the output to a file
    with open('output.out', 'w') as file:
        for line in output_lines:
            file.write(line + '\n')

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
                process_id = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append([arrival, burst, process_id])
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
        if scheduler == "fcfs":
            fifo(runfor, processcount, processes)
        elif scheduler == "sjf":
            sjf(runfor, processcount, processes)
        elif scheduler == "rr":
            if quantum is None:
                print("Error: Missing quantum parameter when use is 'rr'.")
                sys.exit(1)
            rr(runfor, processcount, processes, quantum)
        else:
            print(f"Error: Unknown scheduler '{scheduler}'.")
            sys.exit(1)

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
