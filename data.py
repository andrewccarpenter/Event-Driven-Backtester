#PYTHON PACKAGES

import pandas as pd

#PYTHON MODULES

from abc import (ABCMeta, abstractmethod)
from datetime import datetime
from os.path import (dirname, join, realpath)

#MY MODULES

from Event_Driven_Backtester.events import MarketEvent

#This is an abstract base class and so cannot be instantiated.
#Creates an common interface so that live data feeds can be inputted later
class DataAbstractClass(metaclass = ABCMeta):
    
    #These abstract methods must be redefined in any subclasses to avoid an error.
    #This ensures that all data subclasses are compatible with other classes that communicate with them
    @abstractmethod
    def get_latest_data(self, symbol, N=1):
        pass
    
    @abstractmethod
    def update_data(self):
        pass
    
class HistoricCSVDataHandler(DataAbstractClass):
    
    #Designed to read CSV files for each requested symbol from disk
    #and drip feed data out to mimic live data. 
    
    def __init__(self, event_queue, csv_dir, symbol_list):
        
        #event_queue - the queue on which it pushes MarketEvents
        #csv_dir - Absolute directory path to CSV files.
        #symbol_list - a list of symbol strings
        
        #It is assumed that all files are of the form 'symbol.csv', where symbol
        #is the string in the list.
        
        #DEFAULT CSV_DIR IF NOT GIVEN COULD BE IN THE SAME DIRECTORY??
        
        self.event_queue = event_queue
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {s:[] for s in symbol_list}   #a dictionary containing a list of tuples for each symbol
        
        self.continue_backtest = True
        
        self.initial_symbol_data()     #Load in the CSV file
        
    def initial_symbol_data(self):
        
        #Opens each CSV file and converts each into a DataFrame.
        #Each DataFrame is then put into a dictionary (symbol_data) with the keyword 'symbol'
        
        combined_index = None
        
        for s in self.symbol_list:
            path = join(self.csv_dir, '{}.csv'.format(s))
            self.symbol_data[s] = pd.read_csv(path, index_col = 'date', parse_dates = True)
            #a pandas dataframe with the 'date' column as the row index
        
            #not all assets trade every day, comb_index is a set of ordered unionised dates
            if combined_index is None:
                combined_index = self.symbol_data[s].index
            else:
                combined_index.union(self.symbol_data[s].index)
        
        #reindexes each dataframe and forward fills if there are gaps. Sorts to have the oldest data at the top
        #Creates a generator that iterates through rows
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index = combined_index, method = 'ffill').sort_index().iterrows()
            
    def new_data_generator(self, symbol):
        #a generator that yields the latest row from the data as a tuple:
        #(symbol, datetime, open, high, low, volume, adjusted close)
        
        for row in self.symbol_data[symbol]:
            yield (symbol, row[0],
                   row[1]['open'], row[1]['high'], row[1]['low'], row[1]['volume'], row[1]['adj_close'])
            
    def get_latest_data(self, symbol, N=1):
        #Returns the last N rows from latest_symbol_data - or as many as are available
        
        try:
            return self.latest_symbol_data[symbol][-N:]
        except KeyError:
            print('{} is not a valid symbol'.format(symbol))
        
    def update_data(self):
        #Pushes the latest row into latest_symbol_data for all symbols
        #Adds a MarketEvent to the event_queue to signal this
        
        for s in self.symbol_list:
            try:
                data = next(self.new_data_generator(s))
                self.latest_symbol_data[s].append(data)
            except:
                self.continue_backtest = False   #if there is no data left
            
        self.event_queue.put(MarketEvent())
