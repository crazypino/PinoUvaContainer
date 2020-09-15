#!/usr/bin/env python3
import os 
import pexpect as pct
from multiprocessing import Process
'''
Read me before running:
First of all, open your terminal and make sure you enter root using command "sudo su".
I recommend you check your DNS resolution using "nano /etc/resolv.conf" and add "nameserver 8.8.8.8" to the first uncommented line. "CRTL + O" save change and "CRTL + X" exit.
It is not necessary but I suggest strongly that you can do it to make it run successfully at the first time since Linux environments vary.

Then you need to check your Internet-connected device's name, it is usually "eth0" or "wlan0" and it is "enp39s0" on my device. You can check it by command
"ip a". After knowing your Internet-connected device's name, replace "enp39s0" with yours. You can use ctrl + F to search "enp39s0" in my code and they should
locate at row 85, 87 and 90.

And you should make sure you have installed python3 and package "os", "pexpect" and "multiprocessing". 

After setting these up, you just need to run command "python3 uva_container.py" at the terminal. Then you can open you browser to check http service.
The addresses for two virtual machines are "localhost" and "10.0.3.2", you can use "localhost:8080" and "10.0.3.2:8080" to check them.
And the log files should be located at "/tmp" and "newroot/tmp".

One more thing, since these two log files are totally isolated, you can't check the one at "newroot/tmp" directly though you can check another one at "/tmp". 
You need to use command "chroot newroot" and you will enter the bash at the newroot. Then you can check it by command "nano tmp/http_recorder.log" and this one should be different
with the log at "/tmp".

If you meet any problem while running it, please feel free to contact me by ql2fn@virginia.edu.


'''

def vm1(name):
    print(name, "is working")
    pct.run('mkdir newroot')
    pct.run('mkdir newroot/tmp')
    pct.run('mkdir newroot/uva')
    pct.run('cp -r /lib newroot')
    pct.run('cp -r /lib64 newroot')
    pct.run('cp -r /usr newroot')
    pct.run('cp -r /bin newroot')
    pct.run('cp http_recorder.py newroot/uva')
    
    #os.chdir('newroot/uva')
    
    
    
    
    print("3")
    
    child1 = pct.spawn('chroot newroot /bin/bash -c "python3 uva/http_recorder.py"')
    child1.interact()
    

def vm2(name):
    
    print(name, "is working")
    
    child = pct.spawn('ip netns exec netns0 python3 http_recorder.py')
    child.interact()



def setup():

    ###using namespace and veth pair to isolate network.

    pct.run('ip netns add netns0')

    pct.run('ip netns exec netns0 ip link set lo up')

    pct.run('ip link add veth-default type veth peer name veth-netns0')

    pct.run('ip link set veth-netns0 netns netns0')

    pct.run('ip addr add 10.0.3.1/24 dev veth-default')

    pct.run('ip netns exec netns0 ip addr add 10.0.3.2/24 dev veth-netns0')

    pct.run('ip link set veth-default up')

    pct.run('ip netns exec netns0 ip link set veth-netns0 up')



    pct.run('echo 1 > /proc/sys/net/ipv4/ip_forward')

    pct.run('iptables -A FORWARD -o enp39s0 -i veth-default -j ACCEPT') ##enp39s0 is the Internet-connected device on your linux, you can check it with command "ip a"

    pct.run('iptables -A FORWARD -i enp39s0 -o veth-default -j ACCEPT')

    ### ip masquerading
    pct.run('iptables -t nat -A POSTROUTING -s 10.0.3.2/24 -o enp39s0 -j MASQUERADE')

    ### default gateway
    pct.run('ip netns exec netns0 ip route add default via 10.0.3.1')



if __name__ == '__main__':

    setup()
    p1 = Process(target=vm1, args=('vm1',))
    p1.start()

    p2 = Process(target=vm2, args=('vm2',))
    p2.start()

    p1.join()
    p2.join()
















