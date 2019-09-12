#!/usr/bin/env bash

algs=(
"ccp"
"cubic"
"bbr"
)

losses=(
#0.001
#0.01
#0.1
#1
#2
#5
#10
15
20
)

duration=100

for i in "${algs[@]}"
do
    for j in "${losses[@]}"
    do
        cd /home/lam/Projects/sdccp/ryu/
        pwd
        env PYTHONPATH=/home/lam/Projects/sdccp/ryu/ ./bin/ryu run ryu/app/my_monitor_13.py > build/run.txt 2>&1 &
        PID=$!
        sleep 3s
        echo "sudo python /home/lam/Projects/sdccp/mininet_scripts/competition.py --loss ${j} -c ${i} -t single -d ${duration}"
        sudo python /home/lam/Projects/sdccp/mininet_scripts/competition.py --loss ${j} -c ${i} -t single -d ${duration}
        echo "mv /home/lam/Projects/sdccp/ryu/build/log.txt /home/lam/Projects/sdccp/mininet_scripts/build/utilization2loss/${i}/${j} -f"
        sudo mv /home/lam/Projects/sdccp/ryu/build/log.txt /home/lam/Projects/sdccp/mininet_scripts/build/utilization2loss/${i}/${j} -f

        sleep 2s
        kill -9 ${PID}
        sleep 1s
        sudo mn -c
    done
done

cd /home/lam/Projects/sdccp/mininet_scripts/
cp build/utilization2loss/ccp/* build/utilization2loss/FCA/
sudo ./plot_utilization2loss.py
echo "Exit"
