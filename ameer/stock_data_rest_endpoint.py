__author__ = 'agc'

from flask import Flask, jsonify
import ystockquote
app = Flask(__name__)


@app.route('/stockprice/<stock_ticker>', methods=['GET'])
def get_price(stock_ticker):
    #in production this would be connected to either IQFEEd, dtniq, or IB stock feed if they have one
    # for testing you can either get the current price or implement some form of reading data from a file
    current_price = ystockquote.get_price(str(stock_ticker))
    print current_price
    return current_price

if __name__ == '__main__':
    app.run(debug=True)