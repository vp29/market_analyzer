__author__ = 'Erics'

import plotly.plotly as py
import plotly.graph_objs
import Tkinter as tk
from PIL import ImageTk, Image
from Database import Database
from Helper import Helper
import os
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
import graphs
import time

class Analysis(tk.Frame):
    def __init__(self, parent):
        #tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        list_frame = tk.Frame(self.parent)
        self.lb = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.lb.pack(fill=tk.BOTH, expand=1)
        list_frame.pack(fill=tk.BOTH, expand=1)
        #button_frame = tk.Frame(self.parent)
        get_tables = tk.Button(self.parent, text="Get Tables", command=self.get_tables)
        get_tables.pack(side=tk.RIGHT, padx=5, pady=5)
        get_data = tk.Button(self.parent, text="Get Data", command=self.get_data)
        get_data.pack(side=tk.RIGHT, padx=5, pady=5)
        #button_frame.pack(fill=tk.BOTH, expand=1)

    def get_tables(self):
        db = Database()
        con = db.create_connection()
        cursor = con.cursor()
        cursor.execute("SHOW tables")
        tables = cursor.fetchall()
        self.lb.delete(0, tk.END)
        for table in tables:
            self.lb.insert(tk.END, table)
        con.close()

    def get_data(self):
        items = self.lb.curselection()
        table =  self.lb.get(int(items[0]))[0]
        db = Database(table)
        trades = db.read_trades()
        #print trades
        self.create_window(trades)

    def create_window(self, trades):
        t = tk.Toplevel(self.parent)
        t.wm_title("Window #1")
        tframe = tk.Frame(t)
        tframe.pack(fill=tk.BOTH, expand=1)
        model = TableModel()
        table = TableCanvas(tframe, model=model)
        table.createTableFrame()
        #trades_lb = tk.Listbox(t, selectmode=tk.SINGLE)
        for trade in trades:
            table.addRow(Buy_Time=trade.buy_time, Sell_Time=trade.sell_time, Sell_Price=trade.sell_price,
                         Buy_Price=trade.buy_price, Long_Short=trade.long_short,Trend=trade.actual_type,
                         Exit_URL=trade.exit_url)
        table.redrawTable()
        table.bind('<ButtonRelease-1>', lambda event :self.openPic(event, table))
        analyze_button = tk.Button(t, text="Analyze", command=lambda: self.analyze_data(trades))
        analyze_button.pack(side=tk.RIGHT, padx=5, pady=5)
        bad_trades_button = tk.Button(t, text="View Bad Trades", command=lambda: self.bad_trades(trades, model, table))
        bad_trades_button.pack(side=tk.RIGHT, padx=5, pady=5)
        good_trades_button = tk.Button(t, text="View Good Trades", command=lambda: self.good_trades(trades, model, table))
        good_trades_button.pack(side=tk.RIGHT, padx=5, pady=5)
        all_trades_button = tk.Button(t, text="View All Trades", command=lambda: self.all_trades(trades, model, table))
        all_trades_button.pack(side=tk.RIGHT, padx=5, pady=5)
        #trades_lb.pack(fill=tk.BOTH, expand=1)

    def openPic(self, event, table):
        try:
            rclicked = table.get_row_clicked(event)
            cclicked = table.get_col_clicked(event)
            clicks = (rclicked, cclicked)
            print 'clicks:', clicks
        except:
            print 'Error'
        if clicks:
            #Now we try to get the value of the row+col that was clicked.
            try:
                url = table.model.getValueAt(clicks[0], clicks[1])
                if(url.startswith("https:")):
                    out_file = "temp" + str(time.time()//1) + ".png"
                    graph = graphs.graphs()
                    graph.get_graph(url, out_file)
                    im = Image.open(out_file)
                    im.show()
            except:
                print 'No record at:', clicks


    def analyze_data(self, trades):
        Helper.analyze_db_more_indepth(None, 15000, .5, trades)

    def all_trades(self, trades, model, table):
        model.deleteRows()
        for trade in trades:
            model.addRow(Buy_Time=trade.buy_time, Sell_Time=trade.sell_time, Exit_Cutoff=trade.exit_cutoff,
                         Sell_Price=trade.sell_price, Buy_Price=trade.buy_price, Long_Short=trade.long_short,
                         Trend=trade.actual_type, Exit_URL=trade.exit_url)
        table.redrawTable()

    def bad_trades(self, trades, model, table):
        bad_trades = []
        for trade in trades:
            if trade.buy_price > trade.sell_price:
                bad_trades.append(trade)
        model.deleteRows()
        for trade in bad_trades:
            model.addRow(Buy_Time=trade.buy_time, Sell_Time=trade.sell_time, Exit_Cutoff=trade.exit_cutoff,
                         Sell_Price=trade.sell_price, Buy_Price=trade.buy_price, Long_Short=trade.long_short,
                         Trend=trade.actual_type, Exit_URL=trade.exit_url)
        table.redrawTable()

    def good_trades(self, trades, model, table):
        good_trades = []
        for trade in trades:
            if trade.buy_price < trade.sell_price:
                good_trades.append(trade)
        model.deleteRows()
        for trade in good_trades:
            model.addRow(Buy_Time=trade.buy_time, Sell_Time=trade.sell_time, Exit_Cutoff=trade.exit_cutoff,
                         Sell_Price=trade.sell_price, Buy_Price=trade.buy_price, Long_Short=trade.long_short,
                         Trend=trade.actual_type, Exit_URL=trade.exit_url)
        table.redrawTable()

if __name__ == "__main__":
    root=tk.Tk()
    root.geometry("300x280+300+300")
    Analysis(root)
    root.mainloop()