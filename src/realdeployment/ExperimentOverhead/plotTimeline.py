import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, SecondLocator
import numpy as np
from StringIO import StringIO
import datetime as dt
import matplotlib.collections as collections

# Source mostly taken from http://stackoverflow.com/questions/7684475/plotting-labeled-intervals-in-matplotlib-gnuplot

# Plot function
def timelines(y, xstart, xstop, color='b'):
    """Plot timelines at y from xstart to xstop with given color."""
    plt.hlines(y, xstart, xstop, color, lw=4)
    plt.vlines(xstart, y+0.01, y-0.01, color, lw=2)
    plt.vlines(xstop, y+0.01, y-0.01, color, lw=2)

def plotTimeline(a, filename):
    # Converts str into a datetime object.
    conv = lambda s: dt.datetime.strptime(s, '%H:%M:%S:%f')

    # Use numpy to read the data in.
    data = np.genfromtxt(a, converters={1: conv, 2: conv}, \
                     names=['caption', 'start', 'stop', 'state'], \
                     dtype=None, delimiter=",")
    cap, start, stop = data['caption'], data['start'], data['stop']

    # Check the status, because we paint all lines with the same color
    # together
    is_ok = (data['state'] == 'OK')
    not_ok = np.logical_not(is_ok)

    # Get unique captions and there indices and the inverse mapping
    captions, unique_idx, caption_inv = np.unique(cap, 1, 1)

    # Build y values from the number of unique captions.
    y = (caption_inv + 1) / float(len(captions) + 1)

    # Plot ok tl black
    timelines(y[is_ok], start[is_ok], stop[is_ok], 'k')
    # Plot fail tl red
    timelines(y[not_ok], start[not_ok], stop[not_ok], 'r')

    # Setup the plot
    ax = plt.gca()
    fig = ax.get_figure()
    fig.set_figheight(6)
    fig.set_figwidth(18)
    ax.xaxis_date()
    myFmt = DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_major_locator(SecondLocator(interval=10)) # used to be SecondLocator(0, interval=20)

    plt.axhspan(0.19, 1, facecolor='0.8', alpha=0.5)

    # To adjust the xlimits a timedelta is needed.
    delta = (stop.max() - start.min())/10

    plt.yticks(y[unique_idx], captions, size=14)
    # plt.ylim(0,1)
    plt.tight_layout()
    plt.gcf().subplots_adjust(bottom=0.1)


    plt.xticks(size = 14)
    plt.xlim(start.min()-delta, stop.max()+delta)
    plt.xlabel('Timeline', size=17)
    plt.savefig(filename, format='eps', dpi=200)

if __name__ == "__main__":
    ### Test data
    # a=StringIO("""
    #     Request,10:15:22,10:15:30,OK
    #     Auction Request,10:15:23,10:15:28,OK
    # """)
    '''
    aList = ['Request,10:15:22,10:15:30,OK','Auction Request,10:15:23,10:15:28,OK']
    strVal = "\n".join(aList)
    a = StringIO(strVal)
    '''
    # plotTimeline(a, "test.eps")

    aList = []
    # with open("outputAll.txt", "r") as rH:
    with open("outputAll-unsorted.txt", "r") as rH:
        for line in rH:
            line = line.strip()
            aList.append(line)
    strVal = "\n".join(aList)
    a = StringIO(strVal)
    plotTimeline(a, "overheadGraph.eps")
