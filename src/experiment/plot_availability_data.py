import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle as pkl
from numpy import median, average, std


def create_plot(filename, bucketSize=5, starts=[], stops=[]):
    '''
    Reads data gathered from availability.py and plots the data
    '''
    with open(filename,'rb') as fob:
        activity_log = pkl.load(fob)

    time_t = []
    completed = []

    # organize measurments into 5-second buckets
    for x in range(bucketSize, len(activity_log)):
        if x % bucketSize != 0: continue
        # time is the first entry of the x'th tuple
        time_t.append(activity_log[x][0])
        # completed at time_t is the second entry of the x'th tuple
        # minus the second entry of the (x-1)'th tuple
        completed.append(activity_log[x][1]-activity_log[x-bucketSize][1])

    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"

    label_size = 45
    print("Median: {}".format(median(completed)))
    print("Average: {}".format(average(completed)))
    print("Standard Deviation: {}".format(std(completed)))
    print("Max: {}".format(max(completed)))
    axes = plt.gca()
    axes.set_ylim([0,average(completed)+2*std(completed)])
    axes.set_xlim([0,time_t[-1]])
    axes.tick_params(length=16, width=4)
    lw = 3

    for s in starts:
        plt.axvline(x=s, color = 'green', linewidth=lw, linestyle=':')

    for s in stops:
        plt.axvline(x=s, color = 'red', linewidth=lw, linestyle='--')

    plt.gcf().subplots_adjust(bottom = 0.21, left = 0.20)
    plt.xlabel('Time (seconds)', fontsize = label_size, labelpad=30)
    plt.ylabel('Completed Requests \n per {} Seconds'.format(bucketSize), fontsize = label_size, labelpad=25)

    plt.plot(time_t, completed)
    plt.show()

def main():
    ## NO FAIL
    # fname = "availability_experiment_length-600:delta-1:volume-100:failure_testing-False:poisson-True.pkl"
    # create_plot(fname, 5)

    # # Periodic Failure/Recovery
    # fname = "availability_experiment_length-600:delta-1:volume-100:failure_testing-True:poisson-True.pkl"
    # starts = [120,240,360,480]
    # stops = [60,180,300,420,540]
    # create_plot(fname, 5, starts, stops)

    # # DEADSTOP TEST
    # fname = "availability_experiment_length-600:delta-1:volume-100:failure_testing-d:poisson-True.pkl"
    # starts = [150, 200, 450]
    # stops = [60, 120, 420]
    # create_plot(fname, 5, starts, stops)

    files = ["availability_experiment_length-600:delta-1:volume-100:failure_testing-False:poisson-True.pkl",
            "availability_experiment_length-600:delta-1:volume-100:failure_testing-True:poisson-True.pkl",
            "availability_experiment_length-600:delta-1:volume-100:failure_testing-d:poisson-True.pkl"]

    for f in files:
        with open(f,'rb') as fob:
            activity_log = pkl.load(fob)

            if f == "availability_experiment_length-600:delta-1:volume-100:failure_testing-d:poisson-True.pkl":
                print(f)
                print
                print("before first failure")
                print("throughout: {}".format(activity_log[120][1]))
                print("throughout: {}".format(activity_log[121][1]))
                print("throughout: {}".format(activity_log[122][1]))
                print("throughout: {}".format(activity_log[149][1]))
                print("throughout: {}".format(activity_log[150][1]))
                print("time: {}".format(activity_log[120][0]))
                print("time: {}".format(activity_log[121][0]))
                print("time: {}".format(activity_log[122][0]))
                print("time: {}".format(activity_log[149][0]))
                print("time: {}".format(activity_log[150][0]))

                print("after first failure")
                print("throughout: {}".format(activity_log[420][1]))
                print("throughout: {}".format(activity_log[421][1]))
                print("throughout: {}".format(activity_log[422][1]))
                print("time: {}".format(activity_log[420][0]))
                print("time: {}".format(activity_log[422][0]))

                print("after second failure")
                print("throughout: {}".format(activity_log[-1][1]))
                print("time: {}".format(activity_log[-1][0]))
                print

            else:
                print(f)
                print("throughout: {}".format(activity_log[-1][1]))
                print("time: {}".format(activity_log[-1][0]))


if __name__ == "__main__":
    main()
