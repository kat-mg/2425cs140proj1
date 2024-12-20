class Proc:

    def __init__(self, pid, burst, timeAllotment, arrival, io):
        self.pid = pid
        self.priority = 0
        self.burst = burst
        self.totalBurst = sum(burst)
        self.timeAllotment = timeAllotment
        self.arrival = arrival
        self.io = io
        self.totalIO = sum(io)
        self.endTime = 0
        self.turnaround = 0
        self.waitTime = 0
        self.quantum = 4
    
    def __repr__(self):
        return self.pid

class MLFQ:
    
    def __init__(self, q1TimeAllotment, q2TimeAllotment, contextSwitch):
        self.timeAllotment = [q1TimeAllotment, q2TimeAllotment]
        self.queues = [[], [], []]
        self.prevProc = None                            # Previously run process
        self.contextSwitch = contextSwitch
        self.procs = []
        self.time = 0
        self.running = None
        self.io = []
    
    def addProc(self, proc):
        self.procs.append(proc)

    def addProcToQ1(self, proc):
        self.queues[0].append(proc)

    def printQueuesCPUIODemo(self):
        print(f"Queues : {self.queues[0]};{self.queues[1]};{self.queues[2]}")

        if self.running:
            print("CPU : ", self.running)
        else:
            print("CPU : CS")

        if self.io:
            print("IO : ", self.io)

        print("\nProcesses:")
        for proc in self.procs:
            print(f"{proc.pid} -> Priority: {proc.priority}, Burst: {proc.burst}, "
                f"TimeAllotment: {proc.timeAllotment}, IO: {proc.io}, "
                f"Quantum: {proc.quantum}, Turnaround: {proc.turnaround}, WaitTime: {proc.waitTime}")

        print("")

    def calculateAverageTurnaround(self):
        totalTurnaround = 0
        for proc in self.procs:
            totalTurnaround += proc.turnaround
        return round(totalTurnaround / len(self.procs), 2)
    
    def printOutput(self):
        self.procs.sort(key=lambda x: x.pid)
        for proc in self.procs:
            print(f"Turn-around time for Process {proc.pid} : {proc.endTime} - {proc.arrival} = {proc.turnaround} ms")
        print(f"Average Turn-around time: {self.calculateAverageTurnaround()} ms")
        for proc in self.procs:
            print(f"Waiting time for Process {proc.pid} : {proc.waitTime} ms")

    def run(self):
        willContextSwitch = 0
        finished = False
        while not finished:
            if self.time == 20:
                break
            
            print("At Time = ", self.time)

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

            # Check if current process will give up CPU
            if self.running is not None:
                preempted = False
                print("preempted: ", preempted)
                for i in range(3):
                    if self.queues[i] and self.running.priority < i:
                            self.queues[self.running.priority].append(self.running)
                            self.prevProc = self.running
                            self.running = None
                            willContextSwitch = self.contextSwitch
                            preempted = True
                            break
                
                if not preempted:
                    if self.running.burst[0] == 0:                                             # Process burst finished
                        if self.running.io:                                                    # Process has IO
                            self.io.append(self.running)                                       # Add to IO list
                            if self.running.timeAllotment != 0:                                # If time allotment is 0, reset times
                                self.running.timeAllotment = self.timeAllotment[self.running.priority]
                                self.running.quantum = 4                                        
                            else:
                                self.running.priority += 1                                     # Lower priority
                        if self.running.burst[1:]:                                             # Process has more bursts
                            self.running.burst.pop(0)                                          # Remove the finished burst
                        else:
                            if not self.running.io:                                            # Process has no IO
                                print(self.running.pid, " DONE")                               
                                self.running.turnaround = self.time - self.running.arrival
                                self.running.waitTime = self.running.turnaround - self.running.totalBurst - self.running.totalIO
                                self.running.endTime = self.time
                        self.prevProc = self.running                                           # Assign as previous process
                        self.running = None
                        willContextSwitch = self.contextSwitch

                    elif self.running.timeAllotment == 0 and self.running.priority < 2:        # Time allotment expired
                        self.running.priority += 1                                             # Lower priority
                        self.queues[self.running.priority].append(self.running)                # Move to lower queue
                        if (self.running.priority < 2):                                        # If it's not Q2, set time allotment
                            self.running.timeAllotment = self.timeAllotment[self.running.priority]
                        print(self.running.pid, " DEMOTED")
                        self.prevProc = self.running                                           # Assign as previous process
                        self.running = None                         
                        willContextSwitch = self.contextSwitch

                    elif self.running.priority == 0 and self.running.quantum == 0:             # If it's Q1 (RR) and time quantum expired
                        self.queues[0].append(self.running)                                    # Move to end of Q1
                        self.running.quantum = 4                                               # Reset quantum
                        self.prevProc = self.running                                           # Assign as previous process
                        self.running = None
                        willContextSwitch = self.contextSwitch
                    else:
                        pass          
                else:
                    pass
                
            # Check if IO process will finish
            for proc in self.io[:]:
                if proc.io[0] == 0:                                             # IO burst finished
                    if proc.burst[0] != 0:                                      # If process has bursts left, add back to queue
                        self.queues[proc.priority].append(proc)
                        self.io.remove(proc)
                        proc.io.pop(0)
                    else:                                                       # If process has no bursts left, process is done
                        print(proc.pid, " DONE")                            
                        self.io.remove(proc)
                        proc.io.pop(0)
                        proc.turnaround = self.time - proc.arrival
                        proc.waitTime = proc.turnaround - proc.totalBurst - proc.totalIO
                        proc.endTime = self.time

            # Check next process to run
            current = None
            if self.running is None:
                for i in range(3):
                    if self.queues[i]:
                        current = self.queues[i][0]
                        break

            # Context switch
            if willContextSwitch > 0:
                if current != self.prevProc:                           # If the process is not the previous process, then CS
                    print(f"CONTEXT SWITCHING: {willContextSwitch}ms left")
                    willContextSwitch -= 1
                else:                                                  # If the process is the previous process, then no need to CS                                    
                    willContextSwitch = 0
                    for i in range(3):
                        if self.queues[i]:
                            self.running = self.queues[i].pop(0)
                            break
            else:
                if self.running is None:
                    for i in range(3):
                        if self.queues[i]:
                            self.running = self.queues[i].pop(0)
                            break

            # Subtract time to running process
            if self.running is not None and willContextSwitch == 0:
                self.running.burst[0] -= 1
                self.running.timeAllotment -= 1
                if (self.running.priority == 0):
                    self.running.quantum -= 1
            
            # Subtract time to IO processes
            for proc in self.io:
                proc.io[0] -= 1

            self.printQueuesCPUIODemo()

            # Increment time
            self.time += 1

            if not self.queues[0] and not self.queues[1] and not self.queues[2] and not self.running and not self.io:
                finished = True

        print("SIMULATION DONE \n")
        self.printOutput()


if __name__ == "__main__":

    print("# Enter Scheduler Details #")
    # Get num of procs
    numProc = int(input())
    # Get time allotments for each queue
    timeAllotments = []
    for i in range(2):
        timeAllotment = int(input())
        timeAllotments.append(timeAllotment)
    # Get context switch time
    contextSwitch = int(input())

    # Create MLFQ
    mlfq = MLFQ(timeAllotments[0], timeAllotments[1], contextSwitch)

    # Get proc details
    print("# Enter 3 Process Details #")
    bursts = []
    ios = []
    for i in range(numProc):
        procDeets = input().split(";")
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

    print("# Scheduling Results #")
    mlfq.run()

