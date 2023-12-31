import numpy.random as random
import Events
import ServerCustomer

def GetServer(servers, time, customerType): #get the most available server
    bestServer = None
    bestScore = 0
    serversAvailable = len(servers)

    for s in servers: #compare every server to find the best
        sBusyUntil = s.busyUntil #higher is worse
        
        if time < sBusyUntil: #track if the server is unavailable for treshold blocking
            serversAvailable -= 1

        if time >= sBusyUntil and (bestServer == None or sBusyUntil < bestScore): #if this server is less busy (and exists)
            bestServer = s #least busy server
            bestScore = sBusyUntil

    #blocking treshold
    if customerType == ServerCustomer.NEW and serversAvailable <= 2: #N > 2 then accept the call, otherwise block it (return None)
        bestServer = None
    
    return bestServer

def SimulateM1M2MCC(arrivalRate, handoverRate, serviceRate, timeMax, c):
    #setup
    time = 0
    arrivalsServed = []
    handoversServed = []
    arrivalsBlocked = []
    handoversBlocked = []
    servers = []
    eventList = []

    for i in range(c):
        servers.append(ServerCustomer.Server())

    #simulate
    newArrival = 0
    newHandover = 0
    while time < timeMax:
        #if the server has nothing to do or it is time to generate a customer
        if time >= newArrival or time >= newHandover or len(eventList) == 0 or (len(eventList) > 0 and eventList[0].time > newArrival):
            time = newArrival

            if newArrival < newHandover: #newArrival event
                customer = ServerCustomer.Customer(ServerCustomer.NEW)
                newArrival += float(random.poisson(1/arrivalRate, size=1))
            else: #handover event
                customer = ServerCustomer.Customer(ServerCustomer.HANDOVER)
                newHandover += float(random.poisson(1/handoverRate, size=1))

            eventList = Events.InsertEvent(eventList, Events.Event(Events.ARRIVAL, time, customer))

        #gather event stats
        event = eventList[0] #ARRIVAL, DEPARTURE
        eventType = event.type
        time = event.time #time of event
        customer = event.relevantCustomer #reference to the customer in question

        #depending on the event type, decide what to do
        departureEvent = None #we may have a departure event if we successfully queued a customer
        if eventType == Events.ARRIVAL: #customer has just arrived, assign them to a server
            #find an available server
            nextServer = GetServer(servers, time, customer.type) 
            if nextServer == None: #servers are too busy
                if customer.type == ServerCustomer.NEW: #call blocked
                    arrivalsBlocked.append(customer)
                else: #handover blocked
                    handoversBlocked.append(customer)
            else:
                #assign the customer to the relevant server and start the server processing
                departureEvent = nextServer.Serve(customer, time, serviceRate) #departure event of this customer
        elif eventType == Events.DEPARTURE: #customer has just finished being served
            if customer.type == ServerCustomer.NEW: #call success
                arrivalsServed.append(customer)
            else: #handover success
                handoversServed.append(customer)

        eventList.remove(event)

        if departureEvent != None: 
            eventList = Events.InsertEvent(eventList, departureEvent) #append when the server will be finished with next customer

    #data collection
    cumuServerBusy = 0
    for s in servers:
        cumuServerBusy += s.timeSpentBusy

    cbd = len(arrivalsBlocked) / (len(arrivalsBlocked) + len(arrivalsServed)) #call blocking probability
    hfp = len(handoversBlocked) / (len(handoversBlocked) + len(handoversServed)) #handover failure probability

    return cbd, hfp

#setup
random.seed(5) #set the randomness to be consistent
timeMax = 1000
c = 16 #servers
serviceRate = 100

#simulate
#2.2
arrivalRate = 0.1
handoverRate = 0.0001

highestABP = 0
iterations = 0
while iterations < 99999: #avoid being trapped here forever
    iterations += 1
    cbp, hfp = SimulateM1M2MCC(arrivalRate, handoverRate * iterations, serviceRate, timeMax, c)
    abp = cbp + 10 * hfp #aggregated blocking probability
    
    if abp >= 0.02: #loop until this value exceeds a threshold
        handoverRate *= iterations - 1 #as we have already exceeded the value, the best is iterations-1
        break
    highestABP = abp if abp > highestABP else highestABP #set the new highest

print("Highest handover rate where ABP<0.02:", handoverRate, "with an ABP of:", highestABP) #handover rate 0.0004

#2.3
arrivalRate = 0.0001
handoverRate = 0.03

highestABP = 0
iterations = 0
while iterations < 99999: #avoid being trapped here forever
    iterations += 1
    cbp, hfp = SimulateM1M2MCC(arrivalRate * iterations, handoverRate, serviceRate, timeMax, c)
    abp = cbp + 10 * hfp #aggregated blocking probability
    
    if abp >= 0.02: #loop until this value exceeds a threshold
        arrivalRate *= iterations - 1 #as we have already exceeded the value, the best is iterations-1
        break
    highestABP = abp if abp > highestABP else highestABP #set the new highest

print("Highest arrival rate where ABP<0.02:", arrivalRate, "with an ABP of:", highestABP) #arrival rate 0.001