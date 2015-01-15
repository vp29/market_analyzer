__author__ = 'agc'
import rpyc



class MyService(rpyc.Service):
    test_variable = []

    def on_connect(self):
        pass

    def exposed_keep_connection_alive(self):
        return 1

    def exposed_save_new_assigned_clients(self, assigneditems):
        MyService.exposed_assigned_items_to_clients = []
        MyService.exposed_assigned_items_to_clients = assigneditems
        print("called save new assigned clients, current list of assinged items:")
        print (MyService.exposed_assigned_items_to_clients)



if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port = 18862)
    t.start()
