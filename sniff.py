import scapy.all as scapy

scapy.sniff(filter="udp", prn=lambda x: x.summary(), iface="Software Loopback Interface 1")