import numpy as np
from numpy import mean
from numpy import std
import matplotlib.pyplot as plt
import matplotlib as mpl

def cdf(data_in, n_bins = 50):
    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(figsize=(8, 4))

    # plot the cumulative histogram
    n, bins, patches = ax.hist(data_in, n_bins, normed=1, histtype='step',
                            cumulative=True, linewidth=4, label='Activation time')

    # tidy up the figure
    ax.grid(True)
    #ax.legend(loc='right')
    #ax.set_title('Cumulative step histograms')
    ax.set_xlabel('Time to Active Link (s)')
    ax.set_ylabel('Likelihood of Occurrence')

    #plt.show()
    ax.tick_params(length=16, width=4)
    fig.subplots_adjust(bottom = 0.21, left = 0.20)
    fig.set_size_inches(21.8,12.2)

    plt.savefig("./ping_test/00_ping_test_Results", dpi=166)


# Count the number of time out messages in each ping file
file_num = 100
time_between_extinguish_and_light=10
files = ["ping_test/ping_test_{}".format(x) for x in range(1,file_num)]
timeouts = []
c = 0

for f in files:    
    #print("f = {}".format(f))
    with open(f,'r') as ping_file:
        ping_data = ping_file.readlines()
    

    timeout_count = 0
    for line in ping_data:
        if "Request timeout for icmp_seq" in line:
            timeout_count += 1

    if timeout_count != 50:
        timeouts.append(timeout_count)
        c += 1

    if c == 60:
        break
    
    if timeout_count > 470:
        print(f, timeout_count)

times = [(float(tc)/10.0)-time_between_extinguish_and_light for tc in timeouts]
average = mean(times)
standard_deviation = std(times)
print("max: {}".format(max(times)))
print("min: {}".format(min(times)))
print("mean: {}".format(average))
print("standard deviation: {}".format(standard_deviation))
with open("./ping_test/00_ping_test_Results", 'w') as resultsFile:
    #resultsFile.write("messages set: {}\n".format(messages_sent))
    resultsFile.write("mean time to activate: {} seconds \n".format(average))
    resultsFile.write("standard deviation: {} seconds".format(standard_deviation))

cdf(times)
