#enum implementation for event types
ARRIVAL = 1
DEPARTURE = 2

class Event:
    type = DEPARTURE
    time = 0
    relevantCustomer = None

    def __init__(self, type, time, customer):
        self.type = type
        self.time = time
        self.relevantCustomer = customer
