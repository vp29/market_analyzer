__author__ = 'Erics'
import pymysql
from Trade import Trade

class Database:
    cursor = None
    table_name = ""

    def __init__(self, table_name):
        self.table_name = table_name
        db_connection = self.create_connection()
        self.cursor = db_connection.cursor()
        print table_name
        self.cursor.execute("CREATE TABLE IF NOT EXISTS s" + self.table_name + " (id int PRIMARY KEY NOT NULL AUTO_INCREMENT, "
                       "symbol VARCHAR(20), buy_date INTEGER, sell_date INTEGER, buy_price DOUBLE, "
                       "sell_price DOUBLE, enter_url VARCHAR(256), exit_url VARCHAR(256), actual_type varchar(256), long_short VARCHAR(10));")
        db_connection.commit()
        db_connection.close()

    def insert_trade(self, trade):
        db_connection = self.create_connection()
        self.cursor = db_connection.cursor()
        self.cursor.execute("INSERT INTO s" + self.table_name + "(symbol, buy_date, sell_date, buy_price, sell_price, "
            "enter_url, exit_url, actual_type, long_short) VALUES (\"%s\", %s, %s, %s, %s, \"%s\", \"%s\", \"%s\", \"%s\");" %
            (trade.symbol, trade.buy_time, trade.sell_time, trade.buy_price, trade.sell_price,
             trade.enter_url, trade.exit_url, trade.actual_type, trade.long_short))
        db_connection.commit()
        db_connection.close()

    def read_trades(self):
        trades = []

        db_connection = self.create_connection()
        self.cursor = db_connection.cursor()
        self.cursor.execute("SELECT * FROM s" + self.table_name + " ORDER BY buy_date ASC;")
        for row in self.cursor.fetchall():
            trades.append(Trade(row[2], row[3], 0.0, row[4], row[5], row[9], 0.0, row[1], row[8]))
        db_connection.close()
        return trades

    def create_connection(self):
        return pymysql.connect(host = "stocks1234567.db.9558983.hostedresource.com",
                       port = 3306,
                       user = "stocks1234567",
                       passwd = "Stocktest12345!",
                       db = "stocks1234567")