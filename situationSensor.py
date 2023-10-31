import scapy.all as scapy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--target", type=int, default=39999, help="Target port")
parser.add_argument("-s", "--situation", type=str, required=True, help="Situation")

args = parser.parse_args()

scapy.send(scapy.IP(dst="127.0.0.1")/scapy.UDP(sport=12345, dport=args.target)/scapy.Raw(bytes(args.situation, 'utf-8')))