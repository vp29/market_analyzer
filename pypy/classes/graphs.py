__author__ = 'Erics'

import plotly.plotly as py
import plotly.graph_objs
import Tkinter as tk
from PIL import ImageTk, Image
from Database import Database
from Helper import Helper
import os

#table_name = 's1424992244'
#db = Database(table_name)

class graphs:

    SCALE = 2
    #frame = None
    #canvas = None
    #vsb = None


    def graphs(self, root):
        plotly.tools.set_credentials_file(username='shemer77', api_key='m034bapk2z', stream_ids=['0373v57h06', 'cjbitbcr9j'])

    def get_graph(self, url, out_file):
        figure = py.get_figure(url)
        py.image.save_as(figure, out_file)

"""class Example(tk.Frame):
    SCALE = 2
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.OnFrameConfigure)

        self.show_graph()

    def show_graph(self):
        win = TopLevel()
        panels = []
        images = []

        for i in range(0,4):
            for j in range(0,1):
                pic = Image.open("../plots/graph_" + str(i*1+j) + ".png")
                (width, height) = pic.size
                pic = pic.resize((width/self.SCALE, height/self.SCALE), Image.ANTIALIAS)
                images.append(ImageTk.PhotoImage(pic))

                panels.append(tk.Label(self.frame, image = images[i*1+j]))
                #tk.Label(self.frame, image = images[i*3+j]).grid(row=i, column=j)
                #print i*3+j
                panels[i*1+j].place(x=width/self.SCALE*i + 1, y=height/self.SCALE*j + 1, width=width/self.SCALE, height=height/self.SCALE)
                panels[i*1+j].grid(row=i, column=j)

    def populate(self):
        '''Put in some fake data'''
        for row in range(100):
            tk.Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            t="this is the second colum for row %s" %row
            tk.Label(self.frame, text=t).grid(row=row, column=1)

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

#trades = []
#trades = db.read_trades()
#trades = Helper.order_trades(trades)

#root = tk.Tk()
#graphs(root).pack(side="top", fill="both", expand=True)
#root.mainloop()
#i = 0

root = tk.Tk()

frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

xscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
xscrollbar.grid(row=1, column=0, sticky=tk.E+tk.W)

yscrollbar = tk.Scrollbar(frame)
yscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)

canvas = tk.Canvas(frame, bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

#File = "../plots/graph_0.png"
#img = ImageTk.PhotoImage(Image.open(File))


panels = []
images = []

scale = 1.5

for i in range(0,4):
    for j in range(0,20):
        try:
            pic = Image.open("../plots/graph_" + str(i*3+j) + ".png")
            pic = pic.crop((50,0,550,450))
            (width, height) = pic.size
            swidth = int(width/scale)
            sheight = int(height/scale)
            pic = pic.resize((swidth, sheight), Image.ANTIALIAS)
            images.append(ImageTk.PhotoImage(pic))

            canvas.create_image(swidth*i-100,sheight*j,image=images[i*3+j], anchor="nw")
        except:
            None

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)
canvas.config(scrollregion=canvas.bbox(tk.ALL))
frame.pack(fill="both", expand=True)
root.mainloop()

#if __name__ == "__main__":
#    root=tk.Tk()
#    Example(root).pack(side="top", fill="both", expand=True)
#    root.mainloop()
#for trade in trades:
#    if trade.exit_url != '':
#        graph.get_graph(trade.exit_url, "graph_" + str(i) + ".png")
#        i= i+1"""
