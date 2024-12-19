class Proc:

    def __init__(self, pid, burst, timeAllotment, arrival, io):
        self.pid = pid
        self.priority = 1
        self.burst = burst
        self.timeAllotment = timeAllotment
        self.arrival = arrival
        self.io = io
        self.turnaround = 0
        self.waitTime = 0

class MLFQ:
    
    def __init__(self, q1TimeAllotment, q2TimeAllotment, contextSwitch):
        self.timeAllotment = [q1TimeAllotment, q2TimeAllotment]
        self.queues = [[], [], []]
        self.contextSwitch = contextSwitch
        self.procs = []
        self.time = 0
        self.running = None
        self.io = []

    def add_proc(self, proc):
        self.procs.append(proc)

    def addProc(self, proc):
        self.queues[0].append(proc)

    # TO DO: Implement MLFQ (print output at the same time)

if __name__ == "__main__":

    # Get num of procs
    numProc = int(input("Enter number of processes: "))

    # Get time allotments for each queue
    timeAllotments = []
    for i in range(2):
        print("Enter time allotment for queue", i+1, ": ", end="")
        timeAllotment = int(input())
        timeAllotments.append(timeAllotment)

    # Get context switch time
    contextSwitch = int(input("Enter context switch time: "))

    # Create MLFQ
    mlfq = MLFQ(timeAllotments[0], timeAllotments[1], contextSwitch)

    # Get proc details
    bursts = []
    ios = []
    for i in range(numProc):
        procDeets = input("Enter details for process " + str(i+1) + " (PID, Arrival Time, Burst, I/O): ").split(";")
        pid = procDeets[0]
        arrival = int(procDeets[1])
        for i in range(2, len(procDeets)):
            print(procDeets[i])
            if (i % 2 == 0):
                bursts.append(int(procDeets[i]))
            else:
                ios.append(int(procDeets[i]))

        proc = Proc(pid, bursts, timeAllotments[0], arrival, ios)
        mlfq.add_proc(proc)
        bursts = []
        ios = []
    
    # For testing
    for proc in mlfq.procs:
        print(proc.pid, proc.arrival, proc.burst, proc.io)
    # Test end
