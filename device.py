import scapy.all as scapy
from time import sleep
import socket
import argparse
import threading

def send(l:list, port:int, router:int):
    try:
        while True:
            for dst in l:
                if dst==port:continue
                pkt=scapy.IP(dst="127.0.0.1")/scapy.UDP(sport=port, dport=router)/scapy.UDP(sport=port, dport=dst)/scapy.Raw("A"*10)
                scapy.send(pkt, verbose=False)
                sleep(0.2)
    except KeyboardInterrupt:
        exit()

def recv(port:int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", port))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                print(f"receive from addr:{addr}")
            except socket.error as e:
                if isinstance(e, ConnectionResetError):continue
                if isinstance(e, KeyboardInterrupt):exit()
                print(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=40001, help="port to listen")
    parser.add_argument("-r", "--router", type=int, default=40000, help="port to send")
    parser.add_argument("-l", "--list", nargs="*", default=[40001, 40002, 40003, 40004, 40005, 40006, 40007, 40008], help="port to send")

    args = parser.parse_args()

    t=threading.Thread(target=recv, args=[args.port])
    t.start()
    send(args.list, args.port, args.router)

if __name__=="__main__":
    main()