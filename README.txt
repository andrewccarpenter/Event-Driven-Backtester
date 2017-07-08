Event-Driven Backtester

This backtests trading strategies on historical data - four CSV files of historical tick data are included.

It is ‘event-driven’ in that market data is drip-fed into the system mimicking real life. This is as opposed to a ‘vectorised backtester’ where all of the data is analysed at once. An event-driven backtester allows one to simulate realistic market dynamics and, by connecting to a broker API, could be simply converted to live trading.

This backtester was inspired by the following blogposts:

https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I

loop.py controls the system and requires the following inputs:

CSV_dir: the directory that stores the historical market data
symbol_list: a list containing the names of the CSV files corresponding to stock symbols. E.g. [‘AAPL’, ‘CVX’]

The event-driven logic of loop.py is:

1. updata_data() drips in a new line and puts a MarketEvent() into the queue

2. update_timeindex() updates total positions & holdings based on this new price change

3. calculate_signals() processes the MarketEvent() and puts a new SignalEvent() into the queue. The included strategy is a very simple buy-and-hold strategy. It will never exit a position.

4. update_signal() processes the SignalEvent() and puts a new OrderEvent() into the queue based on the portfolio logic. The included portfolio does no risk management or position sizing.

5. execute_order() processes the OrderEvent() and puts a new FillEvent() into the queue. The broker included executes trades with no commission, latency or slippage in price.

6. update_fill() processes the FillEvent() and updates current positions & holdings.

7. update_timeindex() updates total positions and holdings. No new events are added to the queue so the inner while loop breaks

8. continue looping until all historical data has been used and data.continue_backtest == False.
