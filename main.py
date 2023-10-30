from fogRouter import FogRouter
from rules import *
from entry import *
import scapy.all as scapy
import threading

fog=FogRouter(False)

def parttern(pkt):
    pkt=scapy.IP(dst="127.0.0.1")/scapy.UDP(bytes(pkt["UDP"].payload))
    if fog.allow(str(pkt["UDP"].sport), str(pkt["UDP"].dport)):scapy.send(pkt)
    else:print(f"block: {pkt['UDP'].sport}->{pkt['UDP'].dport}")

def forward():
    scapy.sniff(filter="udp port 40000", prn=parttern, iface="Software Loopback Interface 1", count = 100)

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
    fog.addRule(Rule("notAtHome", [SubRule()], [SubRule()], 1, None, True))
    fog.addRule(Rule("notAtHome1to2", [PathSubRule("/classrooms/classrooms1/")], [PathSubRule("/classrooms/classrooms2/")], 2, None, False), "notAtHome")
    fog.addRule(Rule("notAtHome2to1", [PathSubRule("/classrooms/classrooms2/")], [PathSubRule("/classrooms/classrooms1/")], 2, None, False), "notAtHome")

    fog.addSituation("atHome", ["atHomeExcept1", "atHomeExcept2"])
    fog.addSituation("regular", ["notAtHome1to2", "notAtHome1to2"])
    fog.changeSituation("atHome")
    print(fog.allow("40001", "40002"))

    t=threading.Thread(target=forward)
    t.start()

if __name__ == "__main__":
    main()