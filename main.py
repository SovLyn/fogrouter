from fogRouter import FogRouter
from rules import *
from entry import *
import scapy.all as scapy
import threading
import time
import socket

# 创建一个FogRouter对象，并设置为False
fog=FogRouter(False)
# 初始化总时间和计数器
totalTime=0
count=0

# 打开一个文件，用于记录时间
timeFile=open("time", "w")
# 初始化下一个情况为atHome
nextSituation="atHome"

# 定义一个parttern函数，用于处理数据包
def parttern(pkt):
    global fog
    global totalTime
    global count
    global timeFile
    global nextSituation
    # 将数据包转换为UDP格式
    pkt=scapy.IP(dst="127.0.0.1")/scapy.UDP(bytes(pkt["UDP"].payload))
    # 记录开始时间
    start_time = time.perf_counter()
    # 调用fog的allow函数，检查是否允许访问
    allow =fog.allow(str(pkt["UDP"].sport), str(pkt["UDP"].dport))
    # 记录结束时间
    end_time = time.perf_counter()
    # 计算时间差
    elapsed_time = end_time - start_time
    # 累加时间差
    totalTime+=elapsed_time
    # 计数器加1
    count+=1
    # 每200次计数器，改变情况
    # if count%200==0:
    #     fog.changeSituation(nextSituation)
    #     print(f"change to {nextSituation}")
    #     nextSituation="regular" if nextSituation=="atHome" else "atHome"
    #     timeFile.flush()
    # 打印时间差和平均时间差
    #print(f"time: {elapsed_time}, ave:{totalTime/count}")
    timeFile.write(str(elapsed_time)+"\n")
    # 如果允许访问，则发送数据包
    if allow:scapy.send(pkt, verbose=False)
    # 否则，打印是否被阻止
    else:print(f"block: {pkt['UDP'].sport}->{pkt['UDP'].dport}")

# 定义一个forward函数，用于监听数据包
def forward():
    # 使用scapy监听数据包，并调用parttern函数处理
    scapy.sniff(filter="udp port 40000", prn=parttern, iface="Software Loopback Interface 1", count = 10000)
    # 退出程序
    exit()

# 定义一个main函数，用于添加设备，添加规则，添加情况，改变情况，开启线程，开启socket，开启服务器
def main():
    # 添加设备
    fog.addDevice("/classrooms/classrooms1/sensor1", Entry("40001", "sensor11", ["sensor"]))
    fog.addDevice("/classrooms/classrooms1/sensor2", Entry("40002", "sensor12", ["sensor"]))
    fog.addDevice("/classrooms/classrooms2/sensor1", Entry("40003", "sensor21", ["sensor"]))
    fog.addDevice("/classrooms/classrooms2/sensor2", Entry("40004", "sensor22", ["sensor"]))
    fog.addDevice("/base/sensor/sensor1", Entry("40005", "sensor31", ["sensor"]))
    fog.addDevice("/base/sensor/sensor2", Entry("40006", "sensor32", ["sensor"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("40007", "cellphone1", ["cellphone"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("40008", "cellphone2", ["cellphone"]))

    # 添加规则
    fog.addRule(Rule("atHome", [SubRule()], [SubRule()], 1, None, False))
    fog.addRule(Rule("atHomeExcept1", [PathSubRule("/base/sensor/")], [PathSubRule("/base/sensor/")], 2, None, True), "atHome")
    fog.addRule(Rule("atHomeExcept2", [PathSubRule("/base/cellphone/")], [PathSubRule("/base/sensor/")], 2, None, True), "atHome")
    fog.addRule(Rule("atHomeExcept3", [AliasSubRule("sensor31")], [SubRule()], 3, None, True), "atHome")
    fog.addRule(Rule("notAtHome", [SubRule()], [SubRule()], 1, None, True))
    fog.addRule(Rule("block1to2", [PathSubRule("/classrooms/classrooms1/")], [PathSubRule("/classrooms/classrooms2/")], 2, None, False), "notAtHome")
    fog.addRule(Rule("block2to1", [PathSubRule("/classrooms/classrooms2/")], [PathSubRule("/classrooms/classrooms1/")], 2, None, False), "notAtHome")

    # 添加情况
    fog.addSituation("atHome", ["atHomeExcept1", "atHomeExcept2", "atHomeExcept3"])
    fog.addSituation("regular", ["block1to2", "block2to1"])
    fog.changeSituation("regular")
    # 打印设备列表和规则树
    # print(fog.devices.dumpJSON())
    # print(fog.ruleTree.dumpJSON())

    # 开启线程
    t=threading.Thread(target=forward)
    t.start()
    # 开启socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 39999));
        # 开启服务器
        while True:
            try:
                # 接收数据包
                data, addr = s.recvfrom(1024)
                # 将数据包转换为字符串
                data=data.decode("utf-8")
                print(f"switching to situation:{data}")
                # 改变情况
                fog.changeSituation(data)
            except socket.error as e:
                # 如果出现错误，则跳过
                if isinstance(e, ConnectionResetError):continue
                if isinstance(e, KeyboardInterrupt):exit()
                print(e)

# 调用main函数
if __name__ == "__main__":
    main()