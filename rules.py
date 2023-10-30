import nodeTree
import json

class SubRule:
    def __init__(self):
        pass

    def __str__(self) -> str:
        return f"*"

    def __repr__(self) -> str:
        return self.__str__()
    
    def match(self, target:nodeTree.Node, **kargs) -> bool:
        return True

class OtherSubRule(SubRule):
    def __init__(self):
        pass

    def __str__(self) -> str:
        return f"*"

    def __repr__(self) -> str:
        return self.__str__()

    def match(self, target:nodeTree.Node, **kargs) -> bool:
        return target is None
    
class PathSubRule(SubRule):
    def __init__(self, path:nodeTree.Path|str):
        if isinstance(path, str):
            path=nodeTree.Path(path)
        if not path.abs:
            raise Exception("path must be absolute and dir")
        self.path=path

    def match(self, target:nodeTree.Node, **kargs) -> bool:
        if target is None:return False
        if "nodeTree" not in kargs or not isinstance(kargs["nodeTree"], nodeTree.NodeTree):
            raise Exception("Path rule must get a tree")
        
        p = kargs["nodeTree"].get(self.path)
        if not p: return False
        if not self.path.dir:
            return target==p
        else:
            while target.parent!=p:
                target=target.parent
                if target is None: return False
            return True
        
    def __str__(self) -> str:
        return f"{self.path}"+"*"if self.path.dir else ""
    
    def __expr__(self) -> str:
        return self.__str__()

class TagSubRule(SubRule):
    def __init__(self, tag:list[str]):
        self.tag=tag

    def match(self, target:nodeTree.Node, **kargs) -> bool:
        return any([t in target.content.tags for t in self.tag])
    
    def __str__(self) -> str:
        return self.tag.__str__()
    
    def __expr__(self) -> str:
        return self.__str__()

class AliasSubRule(SubRule):
    def __init__(self, alias:str):
        self.alias=alias

    def match(self, target:nodeTree.Node, **kargs) -> bool:
        if target is None:return False
        return target.content.alias==self.alias
    
    def __str__(self) -> str:
        return f"alias:{self.alias}"
    
    def __expr__(self) -> str:
        return self.__str__()
    
class Rule:
    def __init__(self, name:str, src:list[SubRule], dst:list[SubRule], priority:int, parent:"Rule"=None, allow:bool=False):
        self.name=name
        self.src=src
        self.dst=dst
        self.priority=priority
        self.allow=allow
        self.children=[]
        self.parent=parent
        self.active=False

    def match(self, src:nodeTree.Node, dst:nodeTree.Node, nodeTree:nodeTree.NodeTree) -> bool:
        for r in self.src:
            if r.match(src, nodeTree=nodeTree):break
        else:
            return False
        for r in self.dst:
            if r.match(dst, nodeTree=nodeTree):break
        else:
            return False
        return True
    
    def __str__(self) -> str:
        return f"{self.name}({self.priority}):{self.src} {'o' if self.allow else 'x'}-> {self.dst} {'o' if self.active else 'x'}"
    
    def __expr__(self) -> str:
        return self.__str__()

    def toString(self, indent:int=0) -> str:
        s=f"{' '*indent}{self.__str__()}\n"
        for c in self.children:
            s+=c.toString(indent+2)
        return s
    
    def dumpDict(self) -> dict:
        return {"src":[r.__str__() for r in self.src],
                "dst":[r.__str__() for r in self.dst],
                "priority":self.priority,
                "allow":self.allow,
                "children":[c.dumpDict() for c in self.children]}
    
class RuleTree:
    def __init__(self, default:bool=False):
        self.root=Rule("root", [SubRule()], [SubRule()], 0, None, default)
        self.root.active=True
        self.rules={"root":self.root}

    def addRule(self, rule:Rule, parent:Rule|str=None):
        if isinstance(parent, str):
            parent=self.rules[parent]

        if rule.name in self.rules:
            raise KeyError(f"Rule '{rule.name}' already exists")
        if not parent is None and parent.name not in self.rules:
            raise KeyError(f"Rule '{parent.name}' does not exist")
        if not parent is None and rule.priority<=parent.priority:
            raise ValueError(f"Rule '{rule.name}' has lower priority than '{parent.name}'")

        if parent is None:
            parent=self.root
        rule.parent=parent
        parent.children.append(rule)
        self.rules[rule.name]=rule

    def deactivateAll(self):
        for r in self.rules.values():
            if not r.name=="root":r.active=False

    def activateAll(self):
        for r in self.rules.values():
            r.active=True

    def getRules(self, name:str) -> list[Rule]:
        return [r for r in self.rules.values() if r.name==name]

    def getRule(self, name:str) -> Rule:
        return self.rules[name]
    
    def activate(self, name:str):
        self.getRule(name).active=True
        if self.getRule(name).parent is not None:
            self.activate(self.getRule(name).parent.name)

    def getActiveRules(self) -> list[Rule]:
        return [r for r in self.rules.values() if r.active]

    def deactivate(self, name:str):
        self.getRule(name).active=False

    def dumpDict(self) -> dict:
        return self.root.dumpDict()
    
    def dumpJSON(self) -> str:
        return json.dumps(self.dumpDict())
    
    def __str__(self):
        return self.root.toString(0)
    
    def __repr__(self) -> str:
        return self.__str__()
    
if __name__=="__main__":
    r=RuleTree(False)
    r.addRule(Rule("exam", [SubRule()], [SubRule()], 1, None, False))
    r.addRule(Rule("examExcept1", [PathSubRule("/base/computor/")], [PathSubRule("/base/computor/")], 2, None, True), "exam")
    r.addRule(Rule("examExcept2", [PathSubRule("/base/cellphone/")], [PathSubRule("/base/computor/")], 2, None, True), "exam")
    r.addRule(Rule("lectures", [], [], 1, None, True))
    r.addRule(Rule("classroom1to2", [PathSubRule("/classrooms/classrooms1/")], [PathSubRule("/classrooms/classrooms2/")], 2, None, False), "lectures")
    r.addRule(Rule("classroom2to1", [PathSubRule("/classrooms/classrooms2/")], [PathSubRule("/classrooms/classrooms1/")], 2, None, False), "lectures")
    print(r.dumpJSON())
    print(r)