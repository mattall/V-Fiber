from base.client.tcpclient import TCPClient

def main():
    # Creating the client thread
    client = TCPClient()
    client.start()

    # Wait until the end of processing
    client.join()

if __name__ == '__main__':
    main()
