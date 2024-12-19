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
        self.quantum = 4
    
    def __repr__(self):
        return self.pid

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

    def printQueuesCPUIODemo(self, demoted):
        print("Queues : ",self.queues[0], self.queues[1], self.queues[2])
        print("CPU : ", self.running)       # not sure what should be printed tho if it's context switching
        if self.io:
            print("IO : ", self.io)
        if demoted:
            print(self.running.pid, " DEMOTED")


    # TO DO: Implement MLFQ (print output at the same time)
    def run(self):
        willContextSwitch = 0
        finished = False
        while not finished:
            print("At Time = ", self.time)

            # Remove processes with no burst or io left
            for proc in self.procs:
                if not proc.burst and not proc.io:
                    self.procs.remove(proc)

            # Arrange Q3 for SJF
            self.queues[2].sort(key=lambda x: x.burst[0])

            # Check for new arrivals
            procsArrived = []
            for proc in self.procs:
                if proc.arrival == self.time:
                    procsArrived.append(proc)
            procsArrived.sort(key=lambda x: x.pid)                                         # Sort by proc name in case multiple processes arrive at the same time
            if procsArrived:
                print("Arriving : ", procsArrived)
            for proc in procsArrived:
                self.addProcToQ1(proc)
            procsArrived = []                                                              # Clear the list

            # Check if current process will give up CPU
            demoted = False
            if self.running is not None:
                if self.running.burst[0] == 0:                                             # Process burst finished
                    if self.running.io:                                                    # Process has IO
                        self.io.append(self.running)                                       # Add to IO list
                    if self.running.burst[1:]:                                             # Process has more bursts
                        self.running.burst.pop(0)                                          # Remove the finished burst
                    self.running = None
                    willContextSwitch = self.contextSwitch

                elif self.running.timeAllotment == 0:                                      # Time allotment expired
                    self.running.priority += 1                                             # Lower priority
                    self.queues[self.running.priority].append(self.running)                # Move to lower queue
                    if (self.running.priority <= 1):                                       # If it's Q2
                        self.running.timeAllotment = self.timeAllotment[self.running.priority] # Reset time allotment
                    self.running = None                         
                    willContextSwitch = self.contextSwitch
                    demoted = True

                elif self.queues[0] and self.running.quantum == 0:   # If it's Q1 (RR) and time quantum expired
                    self.queues[0].append(self.running)              # Move to end of Q1
                    self.running.quantum = 4                         # Reset quantum
                    self.running = None
                    willContextSwitch = self.contextSwitch
            else:
                for i in range(3):
                    if (self.queues[i]):
                        self.running = self.queues[i].pop(0)
                        break
            
            # Check if IO process will finish
            for proc in self.io:
                if proc.io[0] == 0:
                    self.queues[proc.priority].append(proc)
                    self.io.remove(proc)                      # Remove the finished IO from the MLFQ IO list
                    proc.io.pop(0)                            # Remove the finished IO from the process IO list
            
            # Check if we need to context switch                 !! BUG: doesnt go here if context switch is 0
            if willContextSwitch > 0:
                if willContextSwitch == self.contextSwitch:
                    willSwitchTo = None
                    for i in range(3):
                        if (self.queues[i]):
                            willSwitchTo = self.queues[i].pop(0)
                            break
                    self.running = willSwitchTo
                willContextSwitch -= 1
            
            # Add time to running process
            if self.running is not None and willContextSwitch == 0:
                self.running.burst[0] -= 1
                self.running.timeAllotment -= 1
                if (self.running.priority == 0):
                    self.running.quantum -= 1
            
            # Add time to IO processes
            for proc in self.io:
                proc.io[0] -= 1

            self.printQueuesCPUIODemo(demoted)

            # Increment time
            self.time += 1

            if not self.queues[0] and not self.queues[1] and not self.queues[2] and not self.running and not self.io:
                finished = True
        print("SIMULATION DONE")


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
    # for proc in mlfq.procs:
    #     print(proc.pid, proc.arrival, proc.burst, proc.io)
    # print(mlfq.timeAllotment)
    # print(mlfq.contextSwitch)
    # Test end

    mlfq.run()
