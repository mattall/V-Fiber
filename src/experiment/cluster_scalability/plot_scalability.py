from os import listdir
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse

def mkGraph(data_in, type_t):
    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(figsize=(8, 4))

    x = [3, 4, 5, 6, 7, 8, 9]

    # plot the cumulative histogram
    ax.plot(x, data_in[80], label="x = 80")
    ax.plot(x, data_in[60], label="x = 60")
    ax.plot(x, data_in[30], label="x = 30")
    ax.plot(x, data_in[10], label="x = 10")
    
    # tidy up the figure
    ax.grid(True)
    #ax.legend(loc='right')
    #ax.set_title('Cumulative step histograms')
    ax.set_xlabel('Cluster Size')
    ax.set_ylabel("Time (s) to Complete 'x' requests")

    #plt.show()
    ax.tick_params(length=16, width=4)
    fig.subplots_adjust(bottom = 0.21, left = 0.20)
    fig.set_size_inches(21.8,12.2)

    legend = ax.legend(loc='upper center', shadow=True, fontsize='small')


    plt.savefig("./results/clusterData_{}".format(type_t), dpi=166)

def main(args):
    files = listdir('.')

    req_size = [10, 30, 60, 80]
    cluster_size = [3, 4, 5, 6, 7, 8, 9]

    rs2cs = {} # request size maps to list of clustersize results
    for r in req_size:
        rs2cs[r] = []

    for r in req_size:
        for c in cluster_size:
            with open("./results/{2}/{0}_{1}_{2}_{3}.txt".format(r, c, args.topology, args.time), 'r') as fob:
                x = fob.readlines()
                x = (float(x[0]) + float(x[1])) / 2
                rs2cs[r].append(x)

    for r in rs2cs:
        print(r, rs2cs[r])

    mkGraph(rs2cs, args.topology)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topology", type=str, help="circuit, two-link, star?")
    parser.add_argument("time", type=str, help="mean, max, or min, 95th percentile?")
    args = parser.parse_args()
    main(args)