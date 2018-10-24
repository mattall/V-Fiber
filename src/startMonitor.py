from monitor.monitor import Monitor

def main():
    switch = '192.168.57.200'
    monitor = Monitor(switch)
    monitor.start_monitor()

if __name__ == '__main__':
    main()