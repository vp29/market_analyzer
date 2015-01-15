__author__ = 'agc'
import rpyc

class ClientService(rpyc.Service):
    def exposed_keep_connection_alive(self):
        return 1



conn = rpyc.connect("localhost",18862, service=ClientService)
print conn
print "connected"
"""
conn.root.exposed_add_stock_to_open_orders_list('tbs',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('aapl1',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('aapl2',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('aapl3',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('aapl4',15.42,18.53)
"""

conn.root.exposed_remove_stock_from_open_orders_list('aapl4')
