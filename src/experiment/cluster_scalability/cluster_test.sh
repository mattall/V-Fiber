for i in 10 30 60 80; do
    for x in {3..9}; do
        echo "$x/9"
        python cluster_scalability_tester.py $x circuit 95th $i
    done
done

for i in 10 30 60 80; do
    for x in {3..9}; do
        echo "$x/9"
        python cluster_scalability_tester.py $x mesh 95th $i
    done
done

for i in 10 30 60 80; do
    for x in {3..9}; do
        echo "$x/9"
        python cluster_scalability_tester.py $x star 95th $i
    done
done