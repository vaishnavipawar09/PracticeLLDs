#Clarifying Questions

#find according to the size and type of file? 

#n-memory vs. persisted? (we’ll assume fully in-memory tree)
#Path style: only absolute Unix-style (e.g. /usr/bin) or support relative/..? (we’ll support only absolute for simplicity)
#Auto-mkdir? when creating directories—skip (we’re only searching)
#Filters: do we need AND vs OR combinations? (yes)
#Metadata fields: just name, size, extension? (yes)

#Are the file system given, or the metadata given?


#Component(ABC)- interface for a file and a directory
#Filter (ABC) - minsize, extension(type)
#FindEngine - Main class

from abc import ABC, abstractmethod
from typing import List, Dict
class Component(ABC):
    def __init__(self, name: str, size: int = 0):
        self.name = name
        self.size = size
        
    @abstractmethod
    def is_directory(self) -> bool:
        pass
    
    
class File(Component):
    def __init__(self, name: str, size: int):
        super().__init__(name, size)
        self.extension = name.split('.')[-1] if '.' in name else ''
        
    def is_directory(self) -> bool:
        return False
        
class Directory(Component):
    def __init__(self, name: str, size: int):
        super().__init__(name, size )
        self.children = Dict[str, Component] = {}
        
    def is_directory(self) -> bool:
        return True
    
    def add(self, comp : Component):
        self.children[comp.name] = comp
        
    def get_child(self, name: str) -> Component:
        return self.children.get(name)
    
class Filter(ABC):
    @abstractmethod
    def matches(self, file: File) -> bool:
        pass
    
class MinSizeFilter(Filter):
    def __init__(self, min_size: int):
        self.min_size = min_size
    def matches(self, file: File) -> bool:
        return file.size >= self.min_size
    
class ExtensionFilter(Filter):
    def __init__(self, ext: str):
        self.ext = ext
    def matches(self, file: File) -> bool:
        return file.extension == self.ext
    
class FindEngine:
    def __init__(self):
        self.filters: List[Filter] = []
        
    def add_filter(self, f: Filter):
        self.filters.append(f)
        
    def find(self, root: Directory, use_and: bool = True) -> List[str]: 
        
        results : List[str] = []
        
        def dfs(node: Component, path: str):
            if node.is_directory():
                for child in node.children.values():
                    dfs(child, f"{path.rstrip('/')}/{child.name}")
                else:
                    file : File = node
                    if use_and:
                        ok = all(f.matches(file) for f in self.filters)                     #matches all the filters
                    else:
                        ok = any(f.matches(file) for f in self.filters)                     #matches atleast one filter
                    if ok:
                        results.append(path)                        #append its full path into results
                        
        dfs(root, "/" if root.name == "/" else "/" + root.name)
        return results
    
if __name__ == "__main__":
    root = Directory("/")                       #create a root directory named /.
    usr=  Directory ("usr"); root.add(usr)      #Under / we add two sub-directories usr and etc.
    bin_dir = Directory("bin"); usr.add(bin_dir)    #inside usr we add bin
    bin_dir.add(File("python", 50))
    bin_dir.add(File("bash", 30))
    etc = Directory("etc"); root.add(etc)
    etc.add(File("hosts", 5))
    
    eng = FindEngine()
    eng.add_filter(MinSizeFilter(30))           #only files > 30 bytes
    eng.add_filter(ExtensionFilter("bash"))    #ionly .bash extension files
    print("AND:", eng.find(root, use_and = True))
    print("OR:", eng.find(root, use_and = False))       # OR: size>=30 OR ext=='bash
    
    

        
    
    
