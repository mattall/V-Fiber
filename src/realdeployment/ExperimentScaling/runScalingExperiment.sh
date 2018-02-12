#!/bin/bash

numberOfInterfaces=5
sliceName="bla"
stitcher="/Applications/omniTools-2.10/stitcher.app/Contents/MacOS/stitcher"
sleepTime=300 #in seconds
output="/Users/ram/Desktop/RAM/Project/GreyFiber/ClientServer/src/realdeployment/ExperimentScaling/scalingOutput-${numberOfInterface}.txt"

echo "#NumberOfInterfaces,#GenerationTime,#TotalTime" > $output

for i in `seq 1 $numberOfInterfaces`;
do
    mkdir $i
    start_time=`date +%s`
    python createCircuit.py --number $i
    end_time_generation=`date +%s`
    mv test-Wisconsin-Missouri-$i.rspec $i/
    cd $i
    $stitcher createsliver $sliceName "test-Wisconsin-Missouri-${i}.rspec" -o
    end_time_creation=`date +%s`
    genTime=`expr $end_time_generation - $start_time`
    totalTime=`expr $end_time_creation - $start_time`
    echo "NumberOfInterface: $i, GenerationTime: $genTime, TotalTime: $totalTime"
    echo "$i,$genTime,$totalTime" >> $output
    echo "" >> $output
    sleep $sleepTime
    $stitcher deletesliver $sliceName
    sleep $sleepTime
    cd ..
done
