#PYTHON PACKAGES

import time
import datetime

#MYMODULES

from queue import Queue
from events import (MarketEvent, SignalEvent, OrderEvent, FillEvent)
from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler

#INSTANTIATIONS

event_queue = Queue()     
CSV_dir = 'INCLUDE DIRECTORY OF CSV FILES HERE'
data = HistoricCSVDataHandler(event_queue, CSV_dir, ['AAPL', 'CVX'])   #Input a list of stock names here
strategy = BuyAndHoldStrategy(data, event_queue)
start_date = datetime.date(14, 12, 1)
portfolio = NaivePortfolio(event_queue, data, start_date)
broker = SimulatedExecutionHandler(event_queue)

#outer loop: mimicking the drip-feed of live data
while True:
    if data.continue_backtest is True:
        data.update_data()    #drip-feed new line of data
    else:
        break
    
    #inner loop: handles events in the queue. Breaks when the queue is empty to get new data
    while True:
        try:
            event = event_queue.get_nowait()     #gets new event but does not wait for queue to fill again if it is empty
        except:                  #raises exception if queue is empty
            break
        
        
        if event is not None:
            if isinstance(event, MarketEvent):
                print('market event')
                portfolio.update_timeindex(event)
                strategy.calculate_signals(event)    #strategy generates signals from market data
                
            elif isinstance(event, SignalEvent):     #portfolio takes signals as advice on how to trade and generates orders based on these
                print('signal event')
                portfolio.update_signal(event)
                
            elif isinstance(event, OrderEvent):     #executes orders
                print('order event')
                broker.execute_order(event)
            
            elif isinstance(event, FillEvent):       #broker tells the portfolio how much of the order was filled
                print('fill event')
                portfolio.update_fill(event)
                portfolio.update_timeindex(event)
    
    print('one step')
    time.sleep(1)    #drip-feed data every 1 second
    
stats = portfolio.output_summary_stats()

print(stats)
