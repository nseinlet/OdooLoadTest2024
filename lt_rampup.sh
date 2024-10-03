#!/bin/bash
if [ -z "$4" ]
  then
      echo "No argument supplied"
      echo "lt.sh test_file nbr_workers base_concurrency time"
      exit 1
fi

declare -a arr=( 0 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190 200 )

for concurrency in "${arr[@]}"
do
    # Launch required number of workers
    x=1
    while [[ $x -le $2 ]]
    do
        locust -f $1 --worker --only-summary > /dev/null 2>&1 &
        x=$(( $x + 1 ))
    done

    usr=$(( $3 + $concurrency ))
    # Launch master and collect datas in csv
    locust -f $1 --headless --users $usr --spawn-rate 1 --run-time $4m --master --expect-workers=$2 --csv=results/$2-$3-$num_test
done
