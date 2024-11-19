


nmcli con add type ethernet ifname eth0 con-name eth0
nmcli con mod eth0 ipv4.addresses 192.168.0.3/24
nmcli con mod eth0 ipv4.gateway 192.168.0.3
nmcli con mod eth0 ipv4.dns 8.8.8.8
nmcli con mod eth0 ipv4.method manual
nmcli con up eth0