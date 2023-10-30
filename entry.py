import nodeTree
from typing import Optional

class Entry:
    def __init__(self, address:str, alias:str, tag:list[str]):
        self.address=address
        self.alias=alias
        self.tag=tag

    def __str__(self) -> str:
        return f"{self.address}(alias:{self.alias})->{self.tag}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def dumpDict(self) -> dict:
        return self.__dict__.copy()
    
if __name__=="__main__":
    devices=nodeTree.NodeTree()
    devices.add("/class/class1/computor", Entry("192.168.3.1", "computor1", ["computor"]))
    devices.add("/class/class1/cellphone", Entry("192.168.3.2", "cellphone1", ["cellphone"]))
    devices.add("/class/class2/computor", Entry("192.168.3.3", "computor2", ["computor"]))
    print(devices.dumpJSON())
