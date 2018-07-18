from numpy import mean, std
data = []
with open("ProcessClientRequest_100.txt") as totalTime_file:
    for line in totalTime_file.readlines():
        data.append(float(line))

print("ProcessClientRequest results (msec)")
print(mean(data))
print(std(data))

data = []
with open("CircuitCreation_100.txt") as totalTime_file:
    for line in totalTime_file.readlines():
        data.append(float(line))

print("CircuitCreation results (msec)")
print(mean(data))
print(std(data))
