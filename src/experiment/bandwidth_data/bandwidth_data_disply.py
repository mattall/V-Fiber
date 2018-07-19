from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
from pickle import dump, load

def parse_experiment_data(dat_file_name):
    '''
    returns filename tuple to reference files saved

    raw data -> (bandwidth_file, transfer_file)
    '''
    # read dat data
    with open(dat_file_name, "r") as fob:
        data_lines = fob.readlines()

    interval = [0]
    transfer = [0]
    bandwidth = [0]

    # parse data file into lists
    for line in data_lines:
        # disregard aggrogate measurments following '-'
        # print("if line[0:3] == '- -': break: {}".format(line[0:3]))
        if line[0:3] == '- -': break

        line_items = line.split()
        if "Accepted connection" in line or "Connecting to" in line:
            partner_id = line_items[3].split('.')[-1]
            print("sender id: {}".format(partner_id))

        if "MBytes" in line:
            data_point = line.split()
            start, end = data_point[2].split('-')
            start = float(start)
            end = float(end)
            # verify we are looking at a one second interval here
            if abs(start - end) <= 1:
                interval.append(end)
                interval_unit = data_point[3]
                transfer.append(float(data_point[4]))
                transfer_unit = data_point[5]
                bandwidth.append(float(data_point[6]))
                bandwidth_unit = data_point[7]
                # print("time: {} \t transfer: {} \t bandwidth: {}".format(\
                #             end  , data_point[4],  data_point[6]))

    bw_file = "bandwidth_output_{}.txt".format(partner_id)
    t_file = "transfer_output_{}.txt".format(partner_id)
    dump(bandwidth, open(bw_file, "wb"))
    dump(transfer, open(t_file, "wb"))

    return(bw_file, t_file)

def plot_bandwidth_data(file_name):

    data = load(open(file_name, 'rb'))

    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    label_size = 60
    axes = plt.gca()
    # axes.set_ylim([0,350])
    # axes.set_xlim([0,240])
    axes.tick_params(length=16, width=4)
    axes.locator_params(nbins=4, axis='y')
    plt.gcf().subplots_adjust(bottom=0.18, left = 0.18)
    plt.xlabel('Time (seconds)', fontsize = label_size)
    plt.ylabel('Bandwidth (MBits/second)', fontsize = label_size)
    plt.plot(data)
    plt.show()

def get_time_to_boost(file_names):
    """ returns the time at which bandwidth boost was observerd """

    # OPEN ALL FILES
    data = []
    for f in file_names:
        data.append(load(open(f, 'rb')))

    # Find the shortest set of entries
    lengths = []
    for d in data:
        lengths.append(len(d))

    max_entries = min(lengths)

    # plot data from each set of entries additivley
    plot_one = np.array(data[0])
    plot_two = []
    for x in range(max_entries):
        plot_two.append(plot_one[x]+data[1][x])
    plot_two = np.array(plot_two)

    if len(file_names) == 4:
        plot_three = []
        for x in range(max_entries):
            plot_three.append(plot_two[x] + data[2][x])
        plot_three = np.array(plot_three)

        plot_four = []
        for x in range(max_entries):
            plot_four.append(plot_three[x] + data[3][x])
        plot_four = np.array(plot_four)

    boost_times = []
    for x in range(2, len(plot_four)):
        if plot_four[x] > (2 * plot_four[x-2])-200:
            boost_times.append(x)

    print(boost_times)
    for t in boost_times:
        print('boost at t = {}'.format(t))
        print t-2, plot_four[t-2]
        print t-1, plot_four[t-1]
        print t, plot_four[t]

def plot_multi_bandwidth_data(file_names):

    # OPEN ALL FILES
    data = []
    for f in file_names:
        data.append(load(open(f, 'rb')))

    # Find the shortest set of entries
    lengths = []
    for d in data:
        lengths.append(len(d))

    max_entries = min(lengths)

    # plot data from each set of entries additivley
    plot_one = np.array(data[0])
    plot_two = []
    for x in range(max_entries):
        plot_two.append(plot_one[x]+data[1][x])
    plot_two = np.array(plot_two)

    if len(file_names) == 4:
        plot_three = []
        for x in range(max_entries):
            plot_three.append(plot_two[x] + data[2][x])
        plot_three = np.array(plot_three)

        plot_four = []
        for x in range(max_entries):
            plot_four.append(plot_three[x] + data[3][x])
        plot_four = np.array(plot_four)

    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    label_size = 60
    axes = plt.gca()
    if len(file_names) == 2:
        axes.set_ylim([0,2000])
    elif len(file_names) == 4:
        axes.set_ylim([0,4000])
    else:
        print("bad input data. Need to plot 2 or 4 sets of data. got {}".format(len(file_names)))
        quit()

    # axes.set_xlim([0,240])
    axes.tick_params(length=16, width=4)
    axes.locator_params(nbins=4, axis='y')
    plt.gcf().subplots_adjust(bottom=0.21, left = 0.18)
    plt.xlabel('Time (seconds)', fontsize = label_size, labelpad=30)
    plt.ylabel('Bandwidth (Mb/s)', fontsize = label_size, labelpad=30)
    plt.axhline(y=1000, color = 'black', label="initial capacity", linestyle='dashed')
    plt.plot(plot_one, color='blue', label="1 client/server pair")
    plt.plot(plot_two, color='green', label="2 client/server pairs")
    if len(file_names) == 4:
        plt.plot(plot_three, color='red', label="3 client/server pairs")
        plt.plot(plot_four, color='purple', label="4 client/server pairs")
    plt.show()

def plot_transfer_data(file_name):
    data = load(file_name)

    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    label_size = 60
    axes = plt.gca()
    # axes.set_ylim([0,350])
    # axes.set_xlim([0,240])
    axes.tick_params(length=16, width=4)
    axes.locator_params(nbins=4, axis='y')
    plt.gcf().subplots_adjust(bottom=0.18, left = 0.18)
    plt.xlabel('Time (seconds)', fontsize = label_size)
    plt.ylabel('Transfer (MBytes)', fontsize = label_size)
    plt.plot(data)
    plt.show()

def main():
    # data_file_names = ["./get_files/4_pairs/2018-06-18T14:04:22_perf_client_192.168.57.4",\
    #                 "./get_files/4_pairs/2018-06-18T14:04:25_perf_client_192.168.57.6",\
    #                 "./get_files/4_pairs/2018-06-18T14:05:02_perf_client_192.168.57.3",\
    #                 "./get_files/4_pairs/2018-06-18T14:05:27_perf_client_192.168.57.7"]

    # data_file_names = ["./get_files/4_pairs/2018-06-19T12:07:08_perf_server_192.168.57.3",\
    #                 "./get_files/4_pairs/2018-06-19T12:07:14_perf_server_192.168.57.4",\
    #                 "./get_files/4_pairs/2018-06-19T12:07:23_perf_server_192.168.57.6",\
    #                 "./get_files/4_pairs/2018-06-19T12:07:29_perf_server_192.168.57.7"]

    # data_file_names = ["./get_files/2018-06-19T14:39:37_perf_server_192.168.57.7",\
    #                 "./get_files/2018-06-19T14:39:40_perf_server_192.168.57.6",\
    #                 "./get_files/2018-06-19T14:39:42_perf_server_192.168.57.4",\
    #                 "./get_files/2018-06-19T14:39:44_perf_server_192.168.57.3"]

    # data_file_names = ["./get_files/2018-06-19T14:41:28.903912_perf_client_192.168.57.15.txt",\
    #                 "./get_files/2018-06-19T14:41:28.904032_perf_client_192.168.57.35.txt",\
    #                 "./get_files/2018-06-19T14:41:28.906981_perf_client_192.168.57.14.txt",\
    #                 "./get_files/2018-06-19T14:41:28.937036_perf_client_192.168.57.12.txt"]

    # data_file_names = ["./2018-06-19T15:29:20.657691_perf_client_192.168.57.35.txt",\
    #                 "./2018-06-19T15:29:20.657691_perf_client_192.168.57.35.txt",\
    #                 "./2018-06-19T15:29:20.657691_perf_client_192.168.57.35.txt",\
    #                 "./2018-06-19T15:29:20.657691_perf_client_192.168.57.35.txt"]

    # data_file_names = ["./get_files/2018-06-20T18:36:05_perf_server_192.168.57.4",\
    #                 "./get_files/2018-06-20T18:36:08_perf_server_192.168.57.7",\
    #                 "./get_files/2018-06-20T18:36:10_perf_server_192.168.57.3",\
    #                 "./get_files/2018-06-20T18:36:11_perf_server_192.168.57.6"]

    ### Version in paper
    # data_file_names = ["./get_files/2018-06-25T12:56:58_perf_server_192.168.57.4",\
    #                 "./get_files/2018-06-25T12:57:16_perf_server_192.168.57.7",\
    #                 "./get_files/2018-06-25T12:57:22_perf_server_192.168.57.3",\
    #                 "./get_files/2018-06-25T12:56:59_perf_server_192.168.57.6"]

    data_file_names = ["./get_files/2018-07-18T17:12:59_perf_server_192.168.57.6",
                        "./get_files/2018-07-18T17:13:00_perf_server_192.168.57.4",
                        "./get_files/2018-07-18T17:13:01_perf_server_192.168.57.3",
                        "./get_files/2018-07-18T17:13:02_perf_server_192.168.57.7"]


    bandwidth_files = []
    transfer_files = []

    print(data_file_names)
    for f in data_file_names:
        dat_bandwidth, dat_transfer = parse_experiment_data(f)
        bandwidth_files.append(dat_bandwidth)
        transfer_files.append(dat_transfer)

    # for f in bandwidth_files:
    #     plot_bandwidth_data(f)

    # plot_multi_bandwidth_data(bandwidth_files)

    get_time_to_boost(bandwidth_files)

main()
