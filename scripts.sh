check version:
dmesg | grep MPTCP
sudo sysctl -w net.mptcp.mptcp_scheduler=redundant
sudo sysctl -w net.mptcp.mptcp_scheduler=default
sudo sysctl -w net.mptcp.mptcp_scheduler=blest
sudo sysctl -w net.mptcp.mptcp_enabled=1
sudo sysctl -a | grep mptcp




echo reno > /proc/sys/net/ipv4/tcp_congestion_control
echo cubic > /proc/sys/net/ipv4/tcp_congestion_control
echo bbr > /proc/sys/net/ipv4/tcp_congestion_control

cat /proc/sys/net/ipv4/tcp_congestion_control