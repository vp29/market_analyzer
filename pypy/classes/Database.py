__author__ = 'Erics'
import sqlite3
from Trade import Trade

class Database:
    db_connection = None
    cursor = None

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.cursor = db_connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stocks (id INTEGER PRIMARY KEY, "
                       "symbol TEXT, buy_date INTEGER, sell_date INTEGER, buy_price DOUBLE, "
                       "sell_price DOUBLE, enter_url TEXT, exit_url TEXT, actual_type TEXT, long_short TEXT);")
        self.db_connection.commit()

    def insert_trade(self, trade):
        self.cursor.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (None, trade.symbol, trade.buy_time, trade.sell_time, trade.buy_price, trade.sell_price, trade.enter_url, trade.exit_url, trade.actual_type, trade.long_short))
        self.db_connection.commit()

    def read_trades(self):
        trades = []

        for row in self.cursor.execute("SELECT * FROM stocks WHERE long_short = 'long' ORDER BY buy_date ASC;"):
            trades.append(Trade(row[2], row[3], 0.0, row[4], row[5], row[9], 0.0, row[1], row[8]))

        return trades