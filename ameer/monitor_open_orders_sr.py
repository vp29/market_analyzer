__author__ = 'agc'
import rpyc
import time
import requests
from decimal import *
getcontext().prec = 2

#variables
max_percentage_risk = 0.01



class ClientService(rpyc.Service):
    def exposed_keep_connection_alive(self):
        return 1



conn = rpyc.connect("localhost",18862, service=ClientService)

while True:
    currently_monitored_stocks = conn.root.exposed_stocks_with_open_orders
    print "-------"
    for stock in currently_monitored_stocks:
        """"ticker name, entry point, exit point", """
        print stock
        ticker_name, entry_price, exit_price = stock
        # check the current price of the stock
        current_price = Decimal(requests.get("http://localhost:5000/stockprice/" + str(ticker_name)).text)
        print "current price: ",  current_price
        
        # if the current price is below our entry point by a certain amount(percentage wise), sell shares and remove the stock from the currently monitored stocks
        price_point_to_exit = entry_price * (1-max_percentage_risk)
        print "price point to exit: ", price_point_to_exit
        if current_price < price_point_to_exit:
            print "sell"
            conn.root.exposed_remove_stock_from_open_orders_list(ticker_name)
            continue

        #if current price is inbetween entry point and exit point do nothing
        if entry_price < current_price < exit_price:
            pass
        
        #if current price is above exit point we either sell the stock or push a trailing stop loss order into IB (I hope you can do that through the api and
        # once you push the trailing stop order you remove it from the list)
    print "_______"
    time.sleep(3)