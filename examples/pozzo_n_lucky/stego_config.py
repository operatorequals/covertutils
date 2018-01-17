

K:_data_:_data_		# Source IP
L:_data_:_data_		# Destination IP

M:_data_:_data_		# Source Port
N:_data_:_data_		# Destination Port

R:_data_:_data_		# Sequence Number
P:_data_:_data_		# Acknowledge Number

Q:_data_:_data_		# IP Identification Field
W:_data_:_data_		# TCP flags

ip_tcp_syn='''
45000014QQQQ000040007aeaKKKKKKKKLLLLLLLL	# IP header
MMMMNNNNRRRRRRRRPPPPPPPP50WW200000000000	# TCP header
'''
