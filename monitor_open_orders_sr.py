__author__ = 'agc'

import rpyc
import time

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

        # check the current price of the stock
        # if the current price is below our entry point by a certain amount(percentage wise), sell shares and remove the stock from the currently monitored stocks
        #if current price is inbetween entry point and exit point do nothing
        #if current price is above exit point we either sell the stock or push a trailing stop loss order into IB (I hope you can do that through the api)
    print "_______"
    time.sleep(3)