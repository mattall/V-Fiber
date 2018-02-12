#!/bin/bash

sliceName="TestScaling"
omni="/Applications/omniTools-2.10/omni.app/Contents/MacOS/omni"
stitcher="/Applications/omniTools-2.10/stitcher.app/Contents/MacOS/stitcher"
sleepTime=400 #in seconds
output="/Users/ram/Desktop/RAM/Project/GreyFiber/ClientServer/src/realdeployment/ExperimentScaling/scalingOutput2-${numberOfInterface}.txt"

# echo "#NumberOfInterfaces,#GenerationTime,#TotalTime" > $output
interfaces=('2') # '2' '3' '4' '5' '10' '20' '30' '40' '50')

for i in "${interfaces[@]}"
do
    echo "Testing creation time for $i interfaces."
    mkdir $i
    start_time=`date +%s`
    time python createCircuit2.py --number $i
    end_time_generation=`date +%s`
    mv test-${i}.rspec $i/
    cd $i
    $omni createsliver -a missouri-ig $sliceName "test-${i}.rspec"
    end_time_creation=`date +%s`
    genTime=`expr $end_time_generation - $start_time`
    totalTime=`expr $end_time_creation - $start_time`
    echo "NumberOfInterface: $i, GenerationTime: $genTime, TotalTime: $totalTime"
    echo "$i,$genTime,$totalTime" >> $output
    echo "" >> $output
    sleep $sleepTime
    $omni deletesliver $sliceName --useSliceAggregates 
    cd ..
done
