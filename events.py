class Event():
    #Abstract base class providing an interface for all inherited events.
    #Allows more events to be added later
    pass

class MarketEvent(Event):
    #New market data
    pass
    
class SignalEvent(Event):
    #Handles the event of sending a signal from the strategy to the portfolio
    
    def __init__(self, symbol, datestamp, signal_type):
        
        #symbol - the ticker symbol e.g. 'GOOG'
        #datetime - the timestamp at which the signal was generated
        #signal_type - 'LONG' or 'SHORT'
        
        self.symbol = symbol
        self.datestamp = datestamp
        self.signal_type = signal_type

class OrderEvent(Event):
    #Handles the event of sending an order from the portfolio to execution
    
    def __init__(self, symbol, order_type, quantity, direction):
        
        #symbol - the ticker symbol e.g. 'GOOG'
        #order_type - 'MARKET', 'LIMIT', 'STOP', 'STOPLIMIT'
        #quantity - non-negative integer
        #direction - 'BUY' or 'SELL'
        
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
    
    def __repr__(self):     #returns a string representation of the object
        return('{cls}({d})'.format(cls = self.__class__, d = self.__dict__))

class FillEvent(Event):
    #Handles the event of an order actually getting filled, as returned from a broker.
    
    def __init__(self, symbol, datestamp, exchange, quantity, direction, fill_cost, commission = 0):
        
        #symbol - the ticker symbol e.g. 'GOOG'
        #datestamp - the time at which the order was filled
        #exchange - the exchange where the order was filled
        #quantity - the quantity that was actually filled
        #direction - 'BUY' or 'SELL'
        #fill_cost - the cost of the trade
        #commission - an optional commission sent from the broker
        
        self.symbol = symbol
        self.datestamp = datestamp
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.commission = commission
