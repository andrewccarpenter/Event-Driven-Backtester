#PYTHON PACKAGES

import pandas as pd
import numpy as np

#PYTHON MODULES

from queue import Queue
from abc import (ABCMeta, abstractmethod)
from datetime import datetime
from math import floor

#MY MODULES

from Event_Driven_Backtester.events import FillEvent, OrderEvent, SignalEvent
from Event_Driven_Backtester.performance import create_sharpe_ratio, create_drawdowns

class PortfolioAbstractClass(metaclass = ABCMeta):
    #Abstract class providing an interface for all inherited strategy objects
    #Handles the positions (quantities) and holdings (market values) of all instruments
    
    @abstractmethod
    def update_signal(self, event):
        pass
    
    @abstractmethod
    def update_fill(self, event):
        pass

class NaivePortfolio(PortfolioAbstractClass):
    
    #Blindly sends orders to a brokerage without any risk management or position sizing
    
    def __init__(self, event_queue, data, start_date, initial_capital = 100000):
        
        #start_date = the start date of the portfolio
        
        self.event_queue = event_queue
        self.data = data
        self.start_date = start_date
        self.initial_capital = initial_capital
        
        self.symbol_list = self.data.symbol_list
        
        self.all_positions = self.construct_all_positions()
        self.current_positions = {s : 0 for s in self.symbol_list}
        
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        
    def construct_all_positions(self):
        
        #Returns a list containing a single dictionary, whose key:value pairs are symbol:0
        #Also adds a datestamp key to each dictionary
        
        position = {s: 0 for s in self.symbol_list}
        position['datestamp'] = self.start_date
        all_positions = [position]
        
        return(all_positions)
    
    def construct_all_holdings(self):
        
        #Returns a list containing a single dictionary, whose key:value pairs are symbol:0
        #Also adds a datestamp key
        #Also adds a cash key - the spare cash in the account after purchases
        #Also adds a commission key - cumulative comission accrued
        #Also adds a a total key - the total equity in the account net any spare cash and open positions
        
        holding = {s: 0 for s in self.symbol_list}
        holding['datestamp'] = self.start_date
        holding['cash'] = self.initial_capital
        holding['commission'] = 0
        holding['total'] = self.initial_capital
        
        all_holdings = [holding]
        
        return(all_holdings)
    
    def construct_current_holdings(self):
        
        #Returns a dictionary for each symbol with a value of zero.
        
        holdings = {s: 0 for s in self.symbol_list}
        holdings['cash'] = self.initial_capital
        holdings['commission'] = 0
        holdings['total'] = self.initial_capital
        
        return(holdings)
        
    def update_timeindex(self, event):
        
        #Updates all_positions & all_holdings when a MarketEvent occurs
        
        #get_latest_data(s) returns a list with a single element: the following tuple:
        #(symbol, datetime, open, high, low, volume, adjusted close)
        
        data = {s: self.data.get_latest_data(s) for s in self.symbol_list}
        
        datestamp = data[self.symbol_list[0]][0][1]  #newest datestamp
        
        #update all positions
        position = {s: self.current_positions[s] for s in self.symbol_list}
        position['datestamp'] = datestamp
        
        self.all_positions.append(position)
        
        #update all_holdings
        
        holding = {s: 0 for s in self.symbol_list}
        holding['datestamp'] = datestamp
        holding['cash'] = self.current_holdings['cash']
        holding['commission'] = self.current_holdings['commission']
        holding['total'] = self.current_holdings['total']
        
        for s in self.symbol_list:
            #estimate market_value by multiplying current position (quantity) by current adj. close price
            market_value = self.current_positions[s]*data[s][0][6]
            holding[s] = market_value
            holding['total'] += market_value #increase the total account equity by the sum of the market_values for each symbol
        
        self.all_holdings.append(holding)
        
    def update_positions_from_fill(self, event):
        
        #Takes a FillEvent from the broker and updates current_positions dictionary by
        #adding/subtracting the correct quantity of shares
        
        #Check whether the fill was a buy or sell
        fill_dir = 0
        
        if event.direction == 'BUY':
            fill_dir = 1
        else:
            fill_dir = -1
            
        self.current_positions[event.symbol] += fill_dir*event.quantity
    
    def update_holdings_from_fill(self, event):
        #Takes a FillEvent from the broker and updates current_holdings dictionary by
        #adding/subtracting the correct cost
        #In reality a broker would give us the event.fill_cost - the price at which the trade was made
        #We will assume that the fill cost is the current adj. close price
        
        #Check whether the fill was a buy or sell
        fill_dir = 0
        
        if event.direction == 'BUY':
            fill_dir = 1
        else:
            fill_dir = -1
            
        fill_cost = self.data.get_latest_data(event.symbol)[0][6]
        cost = fill_dir*fill_cost*event.quantity
        self.current_holdings[event.symbol] += cost   
        self.current_holdings['commission'] += event.commission
        self.current_holdings['cash'] -= (cost + event.commission)
        self.current_holdings['total'] -= (cost + event.commission)
        
    def update_fill(self, event):   
        #updates the portfolio current positions and holdings from a FillEvent
        
        if isinstance(event, FillEvent):
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
    
    def generate_naive_order(self, event):   
        #Receives a SignalEvent from the strategy and generates an OrderEvent for 100 shares
        #No risk management or position sizing considerations
                
        symbol = event.symbol
        signal_type = event.signal_type
        
        mkt_quantity = 100
        current_position = self.current_positions[symbol]
        order_type = 'MARKET'
        
        if signal_type == 'LONG':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        
        elif signal_type == 'SHORT':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
        
        elif signal_type == 'EXIT' and current_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(current_quantity), 'SELL')
            
        elif signal_type == 'EXIT' and current_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(current_quantity), 'BUY')
        
        return(order)

    def update_signal(self, event):   
            #Receives a SignalEvent and creates an OrderEvent based on portfolio logic
            #and puts it in the queue
            
            if isinstance(event, SignalEvent):
                order = self.generate_naive_order(event)
                self.event_queue.put(order)
    
    def create_equity_curve(self):
            #creates a dataframe from the all_holdings list of dictionaries

            curve = pd.DataFrame(self.all_holdings)
            curve.set_index('datestamp', inplace = True)
            
            #creates a new column which calculates the % change/100 from one datestamp to the next
            curve['returns'] = curve['total'].pct_change()
            
            #creates a new column which calculates the scaling from the initial captial to the total for each datestamp
            curve['equity_curve'] = (1.0 + curve['returns']).cumprod()

            return curve
            
    def output_summary_stats(self):
        
        
        #Returns a list of tuples
        
        self.equity_curve = self.create_equity_curve()
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        equity_curve = self.equity_curve['equity_curve']
        
        sharpe_ratio = create_sharpe_ratio(returns)
        max_drawdown, duration = create_drawdowns(self.equity_curve)
        
        stats = [('Total Return', '{}'.format((total_return - 1)*100)), 
                ('Sharpe Ratio', '{}'.format(sharpe_ratio)),
                ('Max Drawdown', '{}'.format(max_drawdown)),
                ('Drawdown Duration', '{}'.format(duration))]
        
        return stats
