#PYTHON PACKAGES

import pandas as pd
import numpy as np

#PYTHON MODULES

from queue import Queue
from abc import (ABCMeta, abstractmethod)
from datetime import datetime

#MY MODULES

from events import (MarketEvent, SignalEvent)

class StrategyAbstractClass(metaclass = ABCMeta):
    #Abstract class providing an interface for all inherited strategy objects
    
    @abstractmethod
    def calculate_signals(self):
        pass

class BuyAndHoldStrategy(StrategyAbstractClass):
    
    #A very simple strategy that goes LONG all of the symbols upon the first market event. It will never exit a position
    #Can be used as a benchmark against which to compare other strategies
    
    def __init__(self, data, event_queue):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.event_queue = event_queue
        self.bought = {s: False for s in self.symbol_list}    #initialise positions for each symbol
        
    def calculate_signals(self, event):
        #Generate a single LONG signal per symbol when the first marketevent occurs
        
        if isinstance(event, MarketEvent):
            for s in self.symbol_list:
                data = self.data.get_latest_data(s)
                if data is not None and len(data)>0:
                    if self.bought[s] == False:
                        signal = SignalEvent(s, data[0][1],   #datetime
                                       'LONG')
                    
                        self.event_queue.put(signal)
                        self.bought[s] = True
