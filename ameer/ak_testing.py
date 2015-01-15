__author__ = 'agc'
import rpyc

class ClientService(rpyc.Service):
    def exposed_keep_connection_alive(self):
        return 1



conn = rpyc.connect("localhost",18862, service=ClientService)
print conn
print "connected"

conn.root.exposed_add_stock_to_open_orders_list('ibm',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('aapl',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('gme',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('F',15.42,18.53)
conn.root.exposed_add_stock_to_open_orders_list('brk.b',15.42,18.53)

#conn.root.exposed_remove_stock_from_open_orders_list('gme')

