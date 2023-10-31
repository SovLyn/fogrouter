from fogRouter import FogRouter
from rules import *
from entry import *
import scapy.all as scapy
import threading
import time
import socket

fog=FogRouter(False)
totalTime=0
count=0

def parttern(pkt):
    global fog
    global totalTime
    global count
    pkt=scapy.IP(dst="127.0.0.1")/scapy.UDP(bytes(pkt["UDP"].payload))
    start_time = time.perf_counter()
    allow =fog.allow(str(pkt["UDP"].sport), str(pkt["UDP"].dport))
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    totalTime+=elapsed_time
    count+=1
    print(f"time: {elapsed_time}, ave:{totalTime/count}")
    if allow:scapy.send(pkt, verbose=False)
    else:print(f"block: {pkt['UDP'].sport}->{pkt['UDP'].dport}")

def forward():
    scapy.sniff(filter="udp port 40000", prn=parttern, iface="Software Loopback Interface 1", count = 1000)
    exit()

def main():
    fog.addDevice("/classrooms/classrooms1/sensor1", Entry("40001", "sensor11", ["sensor"]))
    fog.addDevice("/classrooms/classrooms1/sensor2", Entry("40002", "sensor12", ["sensor"]))
    fog.addDevice("/classrooms/classrooms2/sensor1", Entry("40003", "sensor21", ["sensor"]))
    fog.addDevice("/classrooms/classrooms2/sensor2", Entry("40004", "sensor22", ["sensor"]))
    fog.addDevice("/base/sensor/sensor1", Entry("40005", "sensor31", ["sensor"]))
    fog.addDevice("/base/sensor/sensor2", Entry("40006", "sensor32", ["sensor"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("40007", "cellphone1", ["cellphone"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("40008", "cellphone2", ["cellphone"]))

    fog.addRule(Rule("atHome", [SubRule()], [SubRule()], 1, None, False))
    fog.addRule(Rule("atHomeExcept1", [PathSubRule("/base/sensor/")], [PathSubRule("/base/sensor/")], 2, None, True), "atHome")
    fog.addRule(Rule("atHomeExcept2", [PathSubRule("/base/cellphone/")], [PathSubRule("/base/sensor/")], 2, None, True), "atHome")
    fog.addRule(Rule("atHomeExcept3", [AliasSubRule("sensor11")], [SubRule()], 3, None, True), "atHome")
    fog.addRule(Rule("notAtHome", [SubRule()], [SubRule()], 1, None, True))
    fog.addRule(Rule("block1to2", [PathSubRule("/classrooms/classrooms1/")], [PathSubRule("/classrooms/classrooms2/")], 2, None, False), "notAtHome")
    fog.addRule(Rule("block2to1", [PathSubRule("/classrooms/classrooms2/")], [PathSubRule("/classrooms/classrooms1/")], 2, None, False), "notAtHome")

    fog.addSituation("atHome", ["atHomeExcept1", "atHomeExcept2", "atHomeExcept3"])
    fog.addSituation("regular", ["block1to2", "block2to1"])
    fog.changeSituation("regular")
    print(fog.allow("40001", "40002"))

    t=threading.Thread(target=forward)
    t.start()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 39999));
        while True:
            try:
                data, addr = s.recvfrom(1024)
                data=data.decode("utf-8")
                print(f"switching to situation:{data}")
                fog.changeSituation(data)
            except socket.error as e:
                if isinstance(e, ConnectionResetError):continue
                if isinstance(e, KeyboardInterrupt):exit()
                print(e)

if __name__ == "__main__":
    main()