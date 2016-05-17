cat host_list | \
while read CMD; do
    scp -i Hw3.pem .ssh/authorized_keys ubuntu@$CMD:/home/ubuntu/.ssh/
#    scp  combined.py  ubuntu@$CMD:~
done



# pssh -h server_list -t 100000000 -l ubuntu -A -i "python combined.py
