import numpy.random as random
import Events
import matplotlib.pyplot as plt
import ServerCustomer

def GetServer(servers, time): #get the most available server
    bestServer = None
    bestScore = 0
    for s in servers: #compare every server to find the best
        sBusyUntil = s.busyUntil #higher is worse
        if time >= sBusyUntil and (bestServer == None or sBusyUntil < bestScore): #if this server is less busy (and exists)
            bestServer = s #least busy server
            bestScore = sBusyUntil
    return bestServer

def SimulateMMCC(arrivalRate, serviceRate, timeMax, c):
    #setup
    time = 0
    customersServed = []
    customersBlocked = []
    servers = []
    eventList = []

    for i in range(c):
        servers.append(ServerCustomer.Server())

    #simulate
    newArrival = 0
    while time < timeMax:
        #if the server has nothing to do or it is time to generate a customer
        if time >= newArrival or len(eventList) == 0 or (len(eventList) > 0 and eventList[0].time > newArrival):
            time = newArrival #set the time to the last arrival event (starts at 0)

            customer = ServerCustomer.Customer() #create customer
            eventList = Events.InsertEvent(eventList, Events.Event(Events.ARRIVAL, time, customer)) #add the event to the events list

            newArrival += float(random.poisson(1/arrivalRate, size=1)) #set the next arrival depending on a poisson distribution
            continue #there is a chance that the next event that will occur is still going to be an arrival event so reset the loop

        #gather event stats
        event = eventList[0] #ARRIVAL, DEPARTURE
        eventType = event.type
        time = event.time #time of event
        customer = event.relevantCustomer #reference to the customer in question

        #depending on the event type, decide what to do
        departureEvent = None #we may have a departure event if we successfully queued a customer
        if eventType == Events.ARRIVAL: #customer has just arrived, assign them to a server
            #find an available server
            nextServer = GetServer(servers, time) 
            if nextServer == None: #all servers are busy
                customersBlocked.append(customer)
            else:
                #assign the customer to the relevant server and start the server processing
                departureEvent = nextServer.Serve(customer, time, serviceRate) #departure event of this customer
        elif eventType == Events.DEPARTURE: #customer has just finished being served
            customersServed.append(customer)

        eventList.remove(event)

        if departureEvent != None: 
            eventList = Events.InsertEvent(eventList, departureEvent) #append when the server will be finished

    cumuServerBusy = 0
    for s in servers:
        cumuServerBusy += s.timeSpentBusy

    #data collection
    utilization = cumuServerBusy / (c * timeMax)
    blockingProbability = len(customersBlocked) / (len(customersServed) + len(customersBlocked))

    return utilization, blockingProbability

random.seed(1) #set the randomness to be consistent
timeMax = 1000
c = 16 #servers
serviceRate = 100

arrivalRates = []
serverUtilization = []
blockingProbabilities = []
for i in range(1, 101): #0.1-1
    arrivalRate = 0.001 * i
    util, blocking = SimulateMMCC(arrivalRate, serviceRate, timeMax, c)

    arrivalRates.append(arrivalRate)
    serverUtilization.append(util)
    blockingProbabilities.append(blocking)

#1.3
#maximum input arrivalRate where Blocking Probability < 0.01 is 0.095

#plotting
plt.figure(figsize=(12, 6))

#blocking probability as arrival rate increases
plt.subplot(1, 2, 1)
plt.plot(arrivalRates, blockingProbabilities)
plt.title('Blocking Probability vs Arrival Rate')
plt.xlabel('Arrival Rate (calls/second)')
plt.ylabel('Blocking Probability')
plt.grid(True)

#server utilization as arrival rate increases
plt.subplot(1, 2, 2)
plt.plot(arrivalRates, serverUtilization)
plt.title('Server Utilization vs Arrival Rate')
plt.xlabel('Arrival Rate (calls/second)')
plt.ylabel('Server Utilization')
plt.grid(True)

plt.tight_layout() #compress the image
plt.show(block=True) #pause the program until we close the shown graphs
