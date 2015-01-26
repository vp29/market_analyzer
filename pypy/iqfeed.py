import sys
import socket

def read_historical_data_socket(sock, file, recv_buffer=4096):
    """
    Read the information from the socket, in a buffered
    fashion, receiving only 4096 bytes at a time.

    Parameters:
    sock - The socket object
    recv_buffer - Amount in bytes to receive per read
    """
    buffer = ""
    data = ""
    olddata = ""
    while True:
        data = sock.recv(recv_buffer)
        data = "".join(data.split("\r"))
        data = data.replace(",\n", "\n")[:-1]
        buffer = olddata + data
        file.write(data)

        # Check if the end message string arrives
        if "!E" in buffer:
            break

    # Remove the end message string
    buffer = buffer[:-12]
    return buffer

if __name__ == "__main__":
    # Define server host, port and symbols to download
    host = "127.0.0.1"  # Localhost
    port = 9100  # Historical data socket port
    syms = []
    f = open("NYSE.txt", 'r')
    for line in f:
        syms.append(line[:-1])

    start_date = "20050101 075000"
    interval = "60"
    # Download each symbol to disk
    for sym in syms:
        print "Downloading symbol: %s..." % sym

        # Construct the message needed by IQFeed to retrieve data
        message = "HIT,%s,%s,%s,,,093000,160000,1\n" % (sym, interval, start_date)

        print message
        # Open a streaming socket to the IQFeed server locally
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        f = open("data/nyse/%s-%s-%ssec.csv" % (sym, start_date, interval), "w")

        # Send the historical data request
        # message and buffer the data
        sock.sendall(message)
        data = read_historical_data_socket(sock, f)
        sock.close
        f.close()

        # Remove all the endlines and line-ending
        # comma delimiter from each record
        f = open("data/nyse/%s-%s-%ssec.csv" % (sym, start_date, interval), "r")
        lines = f.readlines()
        f.close()
        w = open("data/nyse/%s-%s-%ssec.csv" % (sym, start_date, interval), "w")
        w.writelines([line for line in lines[:-1]])
        w.close()
        # Write the data stream to disk

        #f.write(data)
        #f.close()