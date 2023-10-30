from typing import Any, Tuple
import re
import json

class Path:
    def __init__(self, path: str) -> None:
        self.path=path.split("/")
        self.abs=self.path[0]==""
        if self.path[0]=="":del self.path[0]
        self.dir=self.path[-1]==""
        if self.path[-1]=="":del self.path[-1]
        for s in self.path:
            if not re.search(r"^(\w+|\.{1,2})$", s):raise ValueError("Invalid path: "+str(path))

    def __str__(self) -> str:
        return ("/"if self.abs else "")+"/".join(self.path)+("/"if self.dir else "")

    def __repr__(self) -> str:
        return str(self)

class Node:
    def __init__(self, name:str, parent:"Node", isLeaf:bool=True, content:Any=None) -> None:
        self.isLeaf=isLeaf
        if not isLeaf:self.children={}
        self.name=name
        self.parent=parent
        if isLeaf:self.content=content

    def __eq__(self, __value: "Node") -> bool:
        return self is __value

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)
    
    def ls(self)->str:
        return "\n".join([str(c) for c in self.children.values()])
    
    def tree(self, level:int=0)->str:
        return "\t"*level+str(self)+"\n"+(("\n".join([c.tree(level+1) for c in self.children.values()])) if not self.isLeaf else "")

    def __getitem__(self, key:str) -> Any:
        return self.children[key]

    def __setitem__(self, key:str, value:Any) -> None:
        self.children[key]=value

    def __contains__(self, key:str) -> bool:
        return key in self.children

    def __str__(self) -> str:
        return f"{self.name}--{'F'if self.isLeaf else 'D'}"+(f"({self.content})" if self.isLeaf else "")
    
    def __repr__(self) -> str:
        return str(self)
    
    def dumpJSON(self) -> str:
        dic={"name":self.name,"isLeaf":self.isLeaf}
        if not self.isLeaf:
            dic["children"]={}
            for c in self.children:
                dic["children"][c]=self.children[c].dumpDict()
            if "parent" in dic:del dic["parent"]
        return json.dumps(dic)
    
    def dumpDict(self) -> dict:
        dic={"isLeaf":self.isLeaf}
        if not self.isLeaf:
            dic["children"]={}
            for c in self.children:
                dic["children"][c]=self.children[c].dumpDict()
            if "parent" in dic:del dic["parent"]
        elif self.content:
            dic["content"]=self.content.dumpDict() if "dumpDict" in self.content.__dir__() else self.content
        return dic
    
    def loadDict(j:dict) -> "Node":
        result=Node("_", None,j["isLeaf"])
        if not j["isLeaf"]:
            for c in j["children"]:
                result.children[c]=Node.loadDict(j["children"][c])
                result.children[c].parent=result
                result.children[c].name=c
        else:
            result.content=j["content"] if "content" in j else None
        return result

class NodeTree:
    def __init__(self, root:Node=None) -> None:
        if not root:
            self.root=Node("root", None,False)
        else:
            self.root=root
            self.root.name="root"
        self.loc=self.root

    def ls(self)->str:
        return self.loc.ls()
    
    def tree(self)->str:
        return self.loc.tree()

    def __getitem__(self, key:str) -> Any:
        return self.loc[key]

    def __setitem__(self, key:str, value:Any) -> None:
        self.loc[key]=value

    def __contains__(self, key:str) -> bool:
        return key in self.loc

    def add(self, path: Path|str, content:Any=None) -> Tuple[bool, Node]:
        if isinstance(path,str):path=Path(path)

        if path.abs:
            loc=self.root
        else:
            loc=self.loc
        
        for i in range(len(path.path)):
            if path.path[i]=="..":
                loc=loc.parent
                continue
            if path.path[i]==".":continue
            if path.path[i] not in loc.children:
                loc.children[path.path[i]]=Node(path.path[i], loc, i==len(path.path)-1 and not path.dir)
            elif loc.children[path.path[i]].isLeaf and i!=len(path.path)-1:
                return False, None
            elif i==len(path.path)-1 and loc.children[path.path[i]].isLeaf!=(not path.dir):
                return False, None
            loc=loc.children[path.path[i]]

        if not path.dir:
            loc.isLeaf=True
            loc.content=content
        return True, loc
    
    def get(self, path:Path|str)->Node:
        if isinstance(path,str):path=Path(path)

        if path.abs:
            loc=self.root
        else:
            loc=self.loc

        for i in range(len(path.path)):
            if path.path[i]=="..":
                loc=loc.parent
                continue
            if path.path[i] not in loc.children:
                return None
            loc=loc.children[path.path[i]]
        return loc

    def remove(self, path:Path|str)->bool:
        if isinstance(path,str):path=Path(path)

        if path.abs:
            loc=self.root
        else:
            loc=self.loc

        for i in range(len(path.path)):
            if path.path[i]=="..":
                loc=loc.parent
                continue
            if path.path[i]==".":
                continue
            if path.path[i] not in loc.children:
                return False
            loc=loc.children[path.path[i]]

        if loc.isLeaf==(not path.dir):
            del loc.parent.children[loc.name]
            return True
        return False
    
    def move(self, src:Path|str, dst:Path|str)->bool:
        if isinstance(src,str):src=Path(src)
        if isinstance(dst,str):dst=Path(dst)

        if not dst.dir:return False
        n = self.get(src)
        if n==None or n.parent==None: return False
        del n.parent.children[n.name]
        self.add(dst)
        self.get(dst).children[n.name]=n
        return True
    
    def goto(self, path: Path|str) -> bool:
        if isinstance(path,str):path=Path(path)

        if path.abs:
            loc=self.root
        else:
            loc=self.loc
        
        for i in range(len(path.path)):
            if path.path[i]=="..":
                loc=loc.parent
                continue
            if path.path[i]==".":continue
            if path.path[i] not in loc.children:
                return False
            loc=loc.children[path.path[i]]
        if loc.isLeaf:return False
        self.loc=loc
        return True
    
    def dumpJSON(self)->str:
        dic=self.root.dumpDict()
        dic["name"]="root"
        return json.dumps(dic)
    
    def loadJSON(j:str) -> "NodeTree":
        j=json.loads(j)
        return NodeTree.loadDict(j)
    
    def loadDict(j:dict) -> "NodeTree":
        return NodeTree(Node.loadDict(j))
    
if __name__=="__main__":
    nodeTree=NodeTree()
    print(nodeTree.add(Path("a1/b1")))
    print(nodeTree.add(Path("a1/b2/c1"), "121"))
    print(nodeTree.add(Path("a1/b2/c2/d/")))
    print(nodeTree.add(Path("a1/b2/c3/f"), "123f"))
    print(nodeTree.add(Path("a2"), "2"))
    print(nodeTree.add(Path("a2/")))
    print(nodeTree.add(Path("a3/b1")))
    print(nodeTree.tree())
    print(nodeTree.goto(Path("a1")))
    print(nodeTree.add(Path("b3/c1"), "131"))
    print(nodeTree.add(Path("b3/c2/d/")))
    print("removing")
    print(nodeTree.remove(Path("../a3/b1")))
    print(nodeTree.ls())
    print(nodeTree.tree())
    print(nodeTree.goto(Path("/")))
    print(nodeTree.tree())
    j=nodeTree.dumpJSON()
    print(j)
    otherTree = NodeTree.loadJSON(j)
    print(otherTree.tree())