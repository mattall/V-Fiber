import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
from pylab import MaxNLocator

def mkGraph(data_in, type_t):
    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(figsize=(8, 4))

    x = [3, 5, 7, 9]

    # plot the cumulative histogram
    ax.plot(x, data_in[10], label="x = 10")
    ax.plot(x, data_in[40], label="x = 40")
    ax.plot(x, data_in[80], label="x = 80")
    
    # tidy up the figure
    ax.grid(True)
    ya = ax.get_yaxis()
    ya.set_major_locator(MaxNLocator(3, integer=True))
    #ax.legend(loc='right')
    #ax.set_title('Cumulative step histograms')
    ax.set_xlabel('Cluster Size')
    ax.set_ylabel("Time (s) to Complete 'x' requests")    
    ax.tick_params(length=16, width=4)
    plt.xticks(x)
    fig.subplots_adjust(bottom = 0.21, left = 0.20, top = 0.8)
    fig.set_size_inches(21.8,12.2)

    legend = ax.legend(loc='upper center', shadow=False, fontsize='small',\
                        bbox_to_anchor=(0.5, 1.22), ncol = 3)
    


    plt.savefig("./results/clusterData_{}".format(type_t), dpi=166)

def main(args):
    req_size = [10, 40, 80]
    cluster_size = [3, 5, 7, 9]

    rs2cs = {} # request size maps to list of clustersize results
    for r in req_size:
        rs2cs[r] = []

    for r in req_size:
        for c in cluster_size:
            with open("./results/{2}/{0}_{1}_{2}_{3}.txt".format(r, c, args.topology, args.time), 'r') as fob:
                x = fob.readlines()
                x = float(x[0])
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