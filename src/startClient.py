import sys
from base.client.tcpclient import TCPClient

def main():
    # check for request file spec
    buyer_file = None

    try:
        buyer_file = sys.argv[1]
        print("GOT A BUYER FILE"+"\n"+"*"*20)
        client = TCPClient(buyer_file)

    except IndexError:
        # Creating the client thread
        client = TCPClient()

    client.start()
    # Wait until the end of processing
    client.join()

if __name__ == '__main__':
    main()
