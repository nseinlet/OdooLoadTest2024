#!/bin/bash
if [ -z "$4" ]
  then
      echo "No argument supplied"
      echo "lt.sh test_file nbr_workers concurrency time [rounds] [spawn_rate]"
      exit 1
fi

nbr_rounds=1
headless_mode='--headless'
if [ -n "$5" ]
  then
    nbr_rounds=$5
    if [[ $5 -le 0 ]]
      then
        headless_mode=''
    fi
fi
if [[ $nbr_rounds -le 0 ]]
  then
    nbr_rounds=1
fi


spawn_rate=1
if [ -n "$6" ]
  then
    spawn_rate=$6
fi
if [[ $spawn_rate -le 0 ]]
  then
    spawn_rate=1
fi

num_test=1
while [[ $num_test -le $nbr_rounds ]]
do
    # Launch required number of workers
    x=1
    while [[ $x -le $2 ]]
    do
        locust -f $1 --worker --only-summary > /dev/null 2>&1 &
        x=$(( $x + 1 ))
    done
    # Launch master and collect datas in csv

    locust -f $1 $headless_mode --users $3 --spawn-rate $spawn_rate --run-time $4m --master --expect-workers=$2 --csv=results/$2-$3-$num_test
    num_test=$(( $num_test + 1 ))
done
