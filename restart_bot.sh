#/bin/bash
sleep 5
/usr/bin/pkill -f bot.py
sleep 1
cd /home/ec2-user/ecomonth/ && /usr/bin/python3 /home/ec2-user/ecomonth/bot.py 2>&1 | tee -a /home/ec2-user/ecomonth/bot.log &
