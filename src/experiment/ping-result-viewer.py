import numpy as np
from numpy import mean, std, percentile
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib as mpl

def cdf(data_in):
    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # plot the cumulative histogram
    N = len(data_in)
    X = np.sort(data_in)
    Y = np.linspace(1/float(N), 1, N)
    plt.plot(X,Y, linewidth=5)
    
    # tidy up the figure
    ax.grid(True)
    #ax.legend(loc='right')
    #ax.set_title('Cumulative step histograms')
    ax.set_xlabel('Time to Active Link (s)')
    ax.set_ylabel('Likelihood of Occurrence')

    #plt.show()
    ax.tick_params(length=16, width=4)
    plt.yticks(np.linspace(0, 1, num=6))
    plt.xticks(np.linspace(np.floor(X[0]), X[-1], num=8))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    fig.subplots_adjust(bottom = 0.21, left = 0.20)
    fig.set_size_inches(21.8,12.2)

    plt.savefig("./ping_test/00_ping_test_Results", dpi=166)


# Count the number of time out messages in each ping file
file_num = 100
time_between_extinguish_and_light=10
files = ["ping_test/ping_test_{}".format(x) for x in range(file_num)]
timeouts = []

c = 0

for f in files[1:]:    
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

# for f in files:    
#     print("f = {}".format(f))
#     with open(f,'r') as ping_file:
#         ping_data = ping_file.readlines()
    
#     timeout_count = 0
#     for line in ping_data:
#         if "Request timeout for icmp_seq" in line:
#             timeout_count += 1
    
#     timeouts.append(timeout_count)

times = [(np.float(tc)/10.0)-time_between_extinguish_and_light for tc in timeouts]

average = mean(times)
standard_deviation = std(times)
print("Measurements       : {}".format(len (times)))
print("max                : {}".format(max(times)))
print("min. . . . . . . . : {}".format(min(times)))
print("mean               : {}".format(average))
print("5th percentile     : {}".format(percentile(times, 5)))
print("50th percentile    : {}".format(percentile(times, 50)))
print("95th percentile    : {}".format(percentile(times, 95)))
print("standard deviation : {}".format(standard_deviation))
with open("./ping_test/00_ping_test_Results", 'w') as resultsFile:
    resultsFile.write("max                : {}\n".format(max(times)))
    resultsFile.write("min. . . . . . . . : {}\n".format(min(times)))
    resultsFile.write("mean               : {}\n".format(average))
    resultsFile.write("5th percentile     : {}\n".format(percentile(times, 5)))
    resultsFile.write("50th percentile    : {}\n".format(percentile(times, 50)))
    resultsFile.write("95th percentile    : {}\n".format(percentile(times, 95)))
    resultsFile.write("standard deviation : {}\n".format(standard_deviation))

cdf(times)
