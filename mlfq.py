class Proc:

    def __init__(self, pid, burst, timeAllotment, arrival, io):
        self.pid = pid
        self.priority = 0
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
    
    def addProc(self, proc):
        self.procs.append(proc)

    def addProcToQ1(self, proc):
        self.queues[0].append(proc)

    # TO DO: Implement MLFQ (print output at the same time)
    def run(self):
        while len(self.queues[0]) > 0 or len(self.queues[1]) > 0 or len(self.queues[2]) > 0 or len(self.io) > 0:
            print("At Time = ", self.time)

            # Check for new arrivals
            procsArrived = []
            for proc in self.procs:
                if proc.arrival == self.time:
                    procsArrived.append(proc)
            procsArrived.sort()                             # Sort by arrival time in case multiple processes arrive at the same time
            if procsArrived:
                print("Arriving : ", procsArrived)
            for proc in procsArrived:
                self.addProcToQ1(proc)
            procsArrived = []                               # Clear the list

            # Check if current process will give up CPU
            willContextSwitch = False
            if self.running is not None:
                if self.running.burst[0] == 0:             # Process finished
                    print(self.running.pid, " DONE")
                    if self.running.io > 0:                # Process has IO
                        self.io.append(self.running)
                    self.running.burst.pop(0)              # Remove the finished burst
                    self.running = None
                    willContextSwitch = True
                elif self.running.timeAllotment == 0:  # Time allotment expired
                    self.running.priority += 1                                             # Lower priority
                    self.queues[self.running.priority].append(self.running)                # Move to lower queue
                    self.running.timeAllotment = self.timeAllotment[self.running.priority] # Reset time allotment
                    self.running = None                         
                    willContextSwitch = True
                elif self.queues[0] and self.time % 4 == 0:   # If it's Q1 (RR) and time quantum expired
                    self.queues[0].append(self.running)       # Move to end of Q1
                    self.running = None
                    willContextSwitch = True
            
            # Check if IO process will finish
            for proc in self.io:
                if proc.io == 0:
                    self.queues[proc.priority].append(proc)
                    self.io.remove(proc)                      # Remove the finished IO from the MLFQ IO list
                    proc.io.pop(0)                            # Remove the finished IO from the process IO list
            
            # Check if we need to context swith
            if willContextSwitch:
                self.time += self.contextSwitch
                willSwitchTo = None
                if self.queues[0]:
                    willSwitchTo = self.queues[0].pop(0)
                elif self.queues[1]:
                    willSwitchTo = self.queues[1].pop(0)
                elif self.queues[2]:
                    willSwitchTo = self.queues[2].pop(0)
                self.running = willSwitchTo
            
            # Add time to running process
            if self.running is not None:
                self.running.burst[0] -= 1
                self.running.timeAllotment -= 1
            
            # Add time to IO processes
            for proc in self.io:
                proc.io -= 1

            # Increment time
            self.time += 1


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
            if (i % 2 == 0):
                bursts.append(int(procDeets[i]))
            else:
                ios.append(int(procDeets[i]))

        proc = Proc(pid, bursts, timeAllotments[0], arrival, ios)
        mlfq.addProc(proc)
        bursts = []
        ios = []
    
    # For testing
    for proc in mlfq.procs:
        print(proc.pid, proc.arrival, proc.burst, proc.io)
    print(mlfq.timeAllotment)
    print(mlfq.contextSwitch)
    # Test end

    mlfq.run()
