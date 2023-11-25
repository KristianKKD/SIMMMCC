import random

ARRIVAL = 1
DEPARTURE = 2

class Customer:
    id = 0 #a 'name' for the customer
    time = 0 #arrivalTime, named this to save me from having to rewrite the same function twice
    departureTime = 0 #time the customer left our system
    serviceStartTime = 0 #time the customer began service (after waiting)
    waitedTime = 0 #time between customer arrival and service
    serviceTime = 0 #time the customer was using our service
    timeInServer = 0 #total time in our servers

    def __init__(self, id, arrivalTime):
        self.id = id
        self.time = arrivalTime

    def Serve(self, startServiceTime, serviceRate):
        self.waitedTime = startServiceTime - self.time
        self.serviceStartTime = startServiceTime
        self.departureTime = startServiceTime + random.expovariate(1 / serviceRate)
        self.serviceTime = self.departureTime - self.serviceStartTime
        self.timeInServer = self.departureTime - self.time
        return self.departureTime

class Event:
    type = DEPARTURE
    time = 0
    relevantCustomer = None
    relevantServer = None

    def __init__(self, type, time, customer, server):
        self.type = type
        self.time = time
        self.relevantCustomer = customer
        self.relevantServer = server

class Channel:
    busyUntil = 0 #time this channel is busy for

    def StartServing(self, customer, startTime, serviceRate): #serve the customer, stop incoming customers from using this channel for some time
        customerDeparture = customer.Serve(startTime, serviceRate) #wait the allotted time
        self.busyUntil = customerDeparture
        return customerDeparture #return the time when the customer will depart

class Server:
    channels = []
    channelsBusy = 0
    queuedCustomers = []

    def __init__(self, capacity):
        for i in range(capacity):
            self.channels.append(Channel())

    def Serve(self, customer, time, serviceRate): #a customer has arrived and has been assigned to this server
        #find an empty channel
        emptyChannel = None
        for c in self.channels:
            if time >= c.busyUntil: #the channel is not busy
                emptyChannel = c
                break
        
        if emptyChannel == None: #if there is no empty channel
            self.queuedCustomers = InsertByVar(self.queuedCustomers, customer) #queue the customer to be assigned later
            return None #we didn't start anything, return nothing
        else: #if we were able to find an empty channel
            customerDeparture = emptyChannel.StartServing(customer, time, serviceRate) #begin service
            self.channelsBusy += 1 #track how many channels are currently in use
            return Event(DEPARTURE, customerDeparture, customer, self) #return a departure event
    
    def FinishedServing(self, time, serviceRate): #a customer is departing from this server
        self.channelsBusy -= 1 #track how many channels are currently in use

        #if we have customers in queue, begin service when we can
        if len(self.queuedCustomers) > 0:
            firstCustomer = self.queuedCustomers[0]
            customerDeparture = self.Serve(firstCustomer, time, serviceRate)
            self.queuedCustomers.remove(firstCustomer)
            return customerDeparture

        return None #we didn't start another service, return nothing
    
    def BusyScore(self): #return how busy this server is, higher means longer time busy
        return self.channelsBusy + len(self.queuedCustomers)

def GetServer(servers): #get the most available server
    bestServer = None
    bestScore = 0
    for s in servers: #compare every server to find the best
        sScore = s.BusyScore() #higher is worse
        if bestServer == None or sScore < bestScore: #if this server is less busy (and exists)
            bestServer = s #this is the server with the lowest queue length that we've seen
            bestScore = sScore
    return bestServer

def InsertByVar(objList, newObj): #insert element in list based on time
    #find relevant position where the obj should be placed
    i = 0
    for i, obj in enumerate(objList):
        if obj.time >= newObj.time: #new element is worse than this element
            break #break and use the i index
        elif i == len(objList) - 1: #this is the highest time
            i += 1 #raise the index so it gets placed at the end

    #insert the new obj in the correct position
    objList.insert(i, newObj)
    return objList

#setup
time = 0
c = 16 #servers
serverCapacity = 8
customersServed = []
servers = []
eventList = []

arrivalRate = 3
serviceRate = 100
timeMax = 3000

for i in range(c):
    servers.append(Server(serverCapacity))

customersInService = 0
nextArrival = 0
while time < timeMax:
    #generate customer
    if nextArrival <= time:
        customersInService += 1
        customer = Customer(customersInService, time)
        nextArrival = time + random.expovariate(1 / arrivalRate)
        eventList = InsertByVar(eventList, Event(ARRIVAL, time, customer, None))

    #if the server has nothing to do, idle until next customer comes, alternatively if it is waiting for too long also have a customer arrive
    if len(eventList) == 0 or (len(eventList) > 0 and eventList[0].time > nextArrival):
        time = nextArrival
        continue

    #gather event stats
    event = eventList[0] #ARRIVAL, DEPARTURE
    eventType = event.type
    time = event.time #time of event
    customer = event.relevantCustomer #reference to the customer in question
    server = event.relevantServer #could be None

    #depending on the event type, decide what to do
    departureEvent = None #we may have a departure event if we successfully queued a customer
    if eventType == ARRIVAL: #customer has just arrived, assign them to a server
        nextServer = GetServer(servers) #get the server with the smallest queue

        #assign the customer to the relevant server and start the server processing if it is the first in queue
        departureEvent = nextServer.Serve(customer, time, serviceRate) #departure event of this customer if it is first in the queue
    elif eventType == DEPARTURE: #customer has just finished being served
        customersServed.append(customer)

        departureEvent = server.FinishedServing(time, serviceRate) #departure event as server starts work on next customer
        #it will return None if there are no customers to serve

    eventList.remove(event)

    if departureEvent != None: 
        eventList = InsertByVar(eventList, departureEvent) #append when the server will be finished


totalTimeWaited = 0.00001
totalTimeServing = 0

for c in customersServed:
    totalTimeWaited += c.waitedTime
    totalTimeServing += c.serviceTime

print(customersInService, customersInService - len(customersServed), totalTimeWaited, totalTimeServing, totalTimeWaited / customersInService, totalTimeServing / customersInService)

print("Done")