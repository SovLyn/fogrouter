from entry import *
from rules import *

class FogRouter:
    def __init__(self, default_allow:bool=False):
        self.devices=nodeTree.NodeTree()
        self.devicesList=dict() #{address:Node}
        self.ruleTree=RuleTree(default_allow)
        self.seen=set() #{address}
        self.situation=dict() #{str:list[str]}
        self.activated=dict() #{priority:list[Rule]}
        self.buffer={}
        self.cur_situation=""

    def getDevice(self, address:str) -> Entry|None:
        return self.devicesList.get(address)

    def getDeviceList(self) -> list[Entry]:
        return list(self.devicesList.values())

    def addSituation(self, name:str, situation:list[str]):
        self.situation[name]=situation

    def addDevice(self, path:nodeTree.Path|str, device:Entry):
        if device.address in self.devicesList:
            raise Exception("Device already exists")
        succeed, node = self.devices.add(path, device)
        if not succeed:
            raise Exception("Could not add device")
        self.devicesList[device.address]=node

    def addRule(self, rule:Rule, parent:Rule|str=None):
        self.ruleTree.addRule(rule, parent)

    def changeSituation(self, situation:str):
        if situation==self.cur_situation:return
        self.cur_situation=situation
        self.buffer={}
        if situation not in self.situation:
            raise Exception("Situation not found")
        self.ruleTree.deactivateAll()
        for rule in self.situation[situation]:self.ruleTree.activate(rule)
        activated=self.ruleTree.getActiveRules()
        self.activated=dict()
        for r in activated:
            if r.priority not in self.activated:self.activated[r.priority]=list()
            self.activated[r.priority].append(r)

    def allow(self, src:str, dst:str) -> bool:
        self.seen.add(src)
        self.seen.add(dst)
        src = self.devicesList[src] if src in self.devicesList else "other"
        dst = self.devicesList[dst] if dst in self.devicesList else "other"

        result=None
        for i in sorted(self.activated.keys(), reverse=True):
            for rule in self.activated[i]:
                if rule.match(src, dst, self.devices):
                    if result is not None:result=rule.allow and result
                    else :result=rule.allow
            #print(rule, result)
            if result is not None:break
        return result
    
    def __str__(self):
        return f"""devices:
{self.devices.tree()}
devicesList:{self.devicesList}
ruleTree:
{self.ruleTree}
seen:{self.seen}
situation:{self.situation}
activated:{self.activated}"""
    
    def __rept__(self):
        return self.__str__()

if __name__ == "__main__":
    fog=FogRouter(False)
    fog.addDevice("/classrooms/classrooms1/computor1", Entry("192.168.3.1", "computor11", ["computor"]))
    fog.addDevice("/classrooms/classrooms1/computor2", Entry("192.168.3.2", "computor12", ["computor"]))
    fog.addDevice("/classrooms/classrooms2/computor1", Entry("192.168.3.3", "computor21", ["computor"]))
    fog.addDevice("/classrooms/classrooms2/computor2", Entry("192.168.3.4", "computor22", ["computor"]))
    fog.addDevice("/base/computor/computor1", Entry("192.168.3.5", "computor31", ["computor"]))
    fog.addDevice("/base/computor/computor2", Entry("192.168.3.6", "computor32", ["computor"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("192.168.3.7", "cellphone1", ["cellphone"]))
    fog.addDevice("/base/cellphone/cellphone", Entry("192.168.3.8", "cellphone2", ["cellphone"]))

    fog.addRule(Rule("exam", [SubRule()], [SubRule()], 1, None, False))
    fog.addRule(Rule("examExcept1", [PathSubRule("/base/computor/")], [PathSubRule("/base/computor/")], 2, None, True), "exam")
    fog.addRule(Rule("examExcept2", [PathSubRule("/base/cellphone/")], [PathSubRule("/base/computor/")], 2, None, True), "exam")
    fog.addRule(Rule("lectures", [SubRule()], [SubRule()], 1, None, True))
    fog.addRule(Rule("classroom1to2", [PathSubRule("/classrooms/classrooms1/")], [PathSubRule("/classrooms/classrooms2/")], 2, None, False), "lectures")
    fog.addRule(Rule("classroom2to1", [PathSubRule("/classrooms/classrooms2/")], [PathSubRule("/classrooms/classrooms1/")], 2, None, False), "lectures")

    fog.addSituation("exam", ["examExcept1", "examExcept2"])
    fog.addSituation("regular", ["classroom1to2", "classroom2to1"])
    fog.changeSituation("exam")
    print(fog)
    print(fog.allow("192.168.3.5", "192.168.3.6"))
    print(fog.allow("192.168.3.6", "192.168.3.5"))
    print(fog.allow("192.168.3.7", "192.168.3.6"))
    print(fog.allow("192.168.3.1", "192.168.3.7"))
    fog.changeSituation("regular")
    print(fog.ruleTree)
    print(fog.allow("192.168.3.1", "192.168.3.4"))
    print(fog.allow("192.168.3.2", "192.168.3.3"))
    print(fog.allow("192.168.3.1", "192.168.3.2"))
    