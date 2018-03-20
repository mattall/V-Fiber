import logging
from settings import CONTEXT, SERVER_BINDING
import time
from datetime import datetime

LOG_FORMAT = '%(created)9.4f %(name)-12s %(levelname)-8s %(message)s'

_loginit = False
def setup_logger(logfile=None):
    global _loginit
    _loginit = True
    loglevel = logging.INFO
    if CONTEXT['debug']:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel, format=LOG_FORMAT)

    applog = logging.getLogger()
    if logfile:
        h = logging.FileHandler(logfile)
        h.setLevel(loglevel)
        h.setFormatter(logging.Formatter(LOG_FORMAT))
        applog.addHandler(h)

def get_logger(name=SERVER_BINDING['service_alias']):
    global _loginit
    if not _loginit:
        setup_logger(None)
    return logging.getLogger(name)

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs

    def printTime(self, module, value, formatNeeded, toFile=False):
        if formatNeeded == "s" and not toFile:
            return "Time in {0} is {1} s.".format(module, value.secs)
        if formatNeeded == "d" and not toFile:
            return "Time in {0} is from {1} to {2}.".format(module, datetime.fromtimestamp(self.start).strftime('%H:%M:%S'),\
                                                           datetime.fromtimestamp(self.end).strftime('%H:%M:%S'))
        if formatNeeded == "d" and toFile:
            return "{0},{1},{2},{3} OK".format(module, datetime.fromtimestamp(self.start).strftime('%H:%M:%S:%f'),\
                                           datetime.fromtimestamp(self.end).strftime('%H:%M:%S:%f'), self.msecs)
