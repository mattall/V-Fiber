# Count the number of time out messages in each ping file
files = ["ping_test/ping_test_{}".format(x) for x in range(file_num)]
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
print("mean: {}".format(average))
print("standard deviation: {}".format(standard_deviation))
with open("./ping_test/0_ping_test_Results", 'w') as resultsFile:
    resultsFile.write("messages set: {}\n".format(messages_sent))
    resultsFile.write("mean time to activate: {} seconds \n".format(average))
    resultsFile.write("standard deviation: {} seconds".format(standard_deviation))
