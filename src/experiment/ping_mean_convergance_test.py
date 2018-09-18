from numpy import mean
from numpy import std
import matplotlib as mpl
import matplotlib.pyplot as plt
total_files = 100
time_between_extinguish_and_light = 0


files = ["absolute_time/ping_test_{}".format(x) for x in range(total_files)]
timeouts = []
for f in files:
    print("f = {}".format(f))
    with open(f,'r') as ping_file:
        ping_data = ping_file.readlines()

    timeout_count = 0
    for line in ping_data:
        if "Request timeout for icmp_seq" in line:
            timeout_count += 1

    timeouts.append(timeout_count)

times = [(float(tc)/10.0)-time_between_extinguish_and_light for tc in timeouts]
average = mean(times)
standard_deviation = std(times)
print(times)
average_over_time = []
for t in range(len(times)):
    if 0 < t:
        average_over_time.append(mean(times[:t]))
##
mpl.rcParams.update({'font.size': 60})
mpl.rcParams['axes.linewidth'] = 4
plt.rcParams["font.family"] = "Times New Roman"
label_size = 60
axes = plt.gca()
axes.tick_params(length=16, width=4)
axes.locator_params(nbins=4, axis='y')
plt.gcf().subplots_adjust(bottom=0.18, left = 0.18)
plt.xlabel('Total Runs', fontsize = label_size)
plt.ylabel('Mean Activation Time', fontsize = label_size)
plt.plot(average_over_time)
plt.show()
##
