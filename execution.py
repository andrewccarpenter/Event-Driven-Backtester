#PYTHON MODULES

from abc import (ABCMeta, abstractmethod)
from datetime import datetime
from queue import Queue

#MY MODULES

from Event_Driven_Backtester.events import FillEvent, OrderEvent

class ExecutionAbstractClass(metaclass = ABCMeta):
    #Abstract class providing an interface for all inherited strategy objects
    
    @abstractmethod
    def execute_order(self, event):
        pass

class SimulatedExecutionHandler(ExecutionAbstractClass):
    
    #Simply converts all OrderEvents to FillEvents with no latency or slippage
    
    def __init__(self, event_queue):
        self.event_queue = event_queue
        
    def execute_order(self, event):
        
        #execute the order on the 'ARCA' exchange
        #the fill_cost is set to None as this is accounted for in the NaivePortfolio
        
        if isinstance(event, OrderEvent):
            fill_event = FillEvent(event.symbol, datetime.now(), 'ARCA',
                                  event.quantity, event.direction, None)
            
            self.event_queue.put(fill_event)
