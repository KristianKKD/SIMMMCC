#enum implementation for event types
ARRIVAL = 1
DEPARTURE = 2

class Event:
    type = ARRIVAL
    time = 0
    relevantCustomer = None

    def __init__(self, type, time, customer): #create an event
        self.type = type
        self.time = time
        self.relevantCustomer = customer

def InsertEvent(eventList, newEvent): #place an event in the relevant position in the list based on time
    #find relevant position where the obj should be placed
    i = 0
    for i, event in enumerate(eventList):
        if event.time >= newEvent.time: #new time is worse than this element
            break #break and use the ith index (the last position)
        elif i == len(eventList) - 1: #this is the highest time
            i += 1 #raise the index so it gets placed at the end of the list

    #insert the new event in the correct position
    eventList.insert(i, newEvent)
    return eventList
