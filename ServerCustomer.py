import numpy.random as random
import Events
#enum implementation for customer types
NEW = 1
HANDOVER = 2

class Customer:
    type = NEW

    def __init__(self, customerType=NEW):
        self.type = customerType

    def ServeCustomer(self, startServiceTime, serviceRate): #simulate service by return an event for when this customer will leave
        return startServiceTime + float(random.exponential(serviceRate, size=1)) #departure time

class Server:
    busyUntil = 0 #time this channel is busy for
    timeSpentBusy = 0 #time this server has been busy for throughout runtime (for data collection)

    def Serve(self, customer, time, serviceRate): #a customer has arrived and has been assigned to this server, serve them
        customerDeparture = customer.ServeCustomer(time, serviceRate) #get the departure time so we can build a departure event
        
        #collect stats
        self.busyUntil = customerDeparture
        self.timeSpentBusy += customerDeparture - time
        
        return Events.Event(Events.DEPARTURE, customerDeparture, customer)

