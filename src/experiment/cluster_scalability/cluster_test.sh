for i in 10 40 80; do
    for x in 3 5 7 9; do
        echo "$x/9"
        python cluster_scalability_tester.py $x darkStrand 95th $i
    done
done


for i in 10 40 80; do
    for x in 3 5 7 9; do
        echo "$x/9"
        python cluster_scalability_tester.py $x circuit 95th $i
    done
done

for i in 10 40 80; do
    for x in 3 5 7 9; do
        echo "$x/9"
        python cluster_scalability_tester.py $x mesh 95th $i
    done
done

for i in 10 40 80; do
    for x in 3 5 7 9; do
        echo "$x/9"
        python cluster_scalability_tester.py $x star 95th $i
    done
done