import numpy.random as random
import Events
#enum implementation for customer types
NEW = 1
HANDOVER = 2

class Customer:
    time = 0 #arrivalTime, named this to save me from having to rewrite the same function twice
    type = NEW
    departureTime = 0 #time the customer left our system
    serviceStartTime = 0 #time the customer began service (after waiting)
    waitedTime = 0 #time between customer arrival and service
    serviceTime = 0 #time the customer was using our service
    timeInServer = 0 #total time in our servers

    def __init__(self, arrivalTime, customerType=NEW):
        self.time = arrivalTime
        self.type = customerType

    def ServeCustomer(self, startServiceTime, serviceRate):
        self.waitedTime = startServiceTime - self.time
        self.serviceStartTime = startServiceTime
        self.departureTime = startServiceTime + float(random.exponential(serviceRate, size=1))
        self.serviceTime = self.departureTime - self.serviceStartTime
        self.timeInServer = self.departureTime - self.time
        return self.departureTime

class Server:
    busyUntil = 0 #time this channel is busy for
    timeSpentBusy = 0

    def Serve(self, customer, time, serviceRate): #a customer has arrived and has been assigned to this server
        customerDeparture = customer.ServeCustomer(time, serviceRate)
        self.busyUntil = customerDeparture
        self.timeSpentBusy += customerDeparture - time
        return Events.Event(Events.DEPARTURE, customerDeparture, customer)

