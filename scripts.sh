check version:
dmesg | grep MPTCP
sudo sysctl -w net.mptcp.mptcp_scheduler=redundant
sudo sysctl -w net.mptcp.mptcp_scheduler=default

