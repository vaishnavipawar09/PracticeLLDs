#Clarifying Questions - File Management system

# 1. Persistence: 
#    - Is this purely in-memory, or do we need to persist files/directories to disk or a database?
# 2. Path Semantics:
#    - Do we need to support only absolute Unix-style paths (e.g. “/usr/bin”) or also relative paths and “.” / “..” navigation?
# 3. Directory Creation:
#    - When creating a directory at “/a/b/c”, should we auto-create missing parents (mkdir –p behavior) or fail if “/a/b” doesn’t exist?
# 4. Deletion Semantics:
#    - Should deleting a non-empty directory recursively remove all its contents, or should we reject unless it’s empty?
# 5. File Content vs. Metadata:
#    - Is managing file contents (read/write) required, or only names and tree structure? Do we need to track timestamps or permissions?
# 6. Naming Rules:
#    - Should names be case-sensitive? Can a file and directory share the same name in one folder?
# 7. Overwrite & Errors:
#    - What happens if we try to create a file or directory that already exists? Return an error, overwrite, or no-op?
# 8. Concurrency:
#    - Will multiple threads access the file system concurrently? If so, which operations must be atomic (e.g., move, delete)?

# These 8 questions cover the critical design boundaries without overwhelming detail. Feel free to adjust or dive deeper once these are clarified. ```

# ✅ Verbal Design Pitch:
# We need a basic file management system that supports:
#  - Files and directories in a hierarchical tree
#  - Operations: create file/dir, delete, move, list directory contents, search by name
#  - Uniform interface for files and directories via Composite pattern
#  - Central access through a singleton FileSystem
#
# Core Classes:
# 1. Component (abstract) — common interface for File and Directory
# 2. File — leaf node, holds just a name
# 3. Directory — composite node, contains child Components
# 4. FileSystem (singleton) — manages the root directory and exposes operations

from abc import ABC, abstractmethod
from typing import List, Dict

#Defines the common interface shared by both files and directories, client can treat files and directories uniformly 
class Component(ABC):
    """Abstract base for File and Directory."""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def is_directory(self) -> bool:
        pass

class File(Component):                  #A terminal node in our tree—cannot contain other Components.
    """Leaf node: no children."""
    def __init__(self, name: str):
        super().__init__(name)          #Carries only its name; any content or metadata could be added later if needed.

    def is_directory(self) -> bool:
        return False                    #Always returns False for is_directory().

class Directory(Component):
    """Composite node: can contain Files and other Directories."""
    def __init__(self, name: str):
        super().__init__(name)
        self.children: Dict[str, Component] = {}

    def is_directory(self) -> bool:                 #is a directory returns True
        return True

    def add(self, comp: Component):                 ## """Add a File or Directory under this directory."""
        self.children[comp.name] = comp

    def remove(self, name: str):                    #"""Remove a child by name."""
        if name in self.children:
            del self.children[name]

    def get(self, name: str) -> Component:          #"""Retrieve a child by name, or None if not found."""
        return self.children.get(name)

    def list_children(self) -> List[str]:           #"""Return all child names (unsorted)."""
        return list(self.children.keys())

class FileSystem:
    """Singleton entry point to manage the tree under a single root directory."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.root = Directory("/")  # root directory

    def _traverse(self, path: str):
        """
        Traverse to the parent directory of `path`.
        Returns (parent_dir, target_name), or (None, None) if invalid.
        """
        if not path.startswith("/") or path == "/":             #if path doesnt start with / return None
            return None, None
        parts = [p for p in path.strip("/").split("/") if p]    #path.strip("/") removes any leading/trailing slashes., split("/") breaks it on / into segments., The list comprehension filters out any empty strings (in case of double-slashes).
        cur = self.root                                         #start at root 
        for name in parts[:-1]:                                 #Traverse all but the last segment
            next_comp = cur.get(name)                           #cur.get(name) looks up that child in the current directory’s map
            if not next_comp or not next_comp.is_directory():   #If there’s no such child, or it exists but isn’t a directory, we again abort with (None, None).
                return None, None
            cur = next_comp  # type: Directory
        return cur, parts[-1]           #Once the loop finishes, cur refers to the directory that should contain our target. parts[-1] is the “leaf” name we want to create, delete, move, etc.

    def create_file(self, path: str) -> bool:
        parent, name = self._traverse(path)                 #checks if the parent and name is in the parent.children, if not add it i the file
        if not parent or name in parent.children:
            return False
        parent.add(File(name))
        return True

    def create_directory(self, path: str) -> bool:          #checks if the parent and name is in the parent.children, if not add it in the directory
        parent, name = self._traverse(path)     
        if not parent or name in parent.children:
            return False
        parent.add(Directory(name))
        return True

    def delete(self, path: str) -> bool:                    #checks if the parent and name is in the parent.children, if yes remove it 
        parent, name = self._traverse(path)
        if not parent or name not in parent.children:
            return False
        parent.remove(name)
        return True

    def move(self, src: str, dst: str) -> bool:
        src_parent, src_name = self._traverse(src)
        dst_parent, dst_name = self._traverse(dst)
        if (not src_parent or not dst_parent or
            src_name not in src_parent.children or
            dst_name in dst_parent.children):               #edge cases, oidf no sorce, or no destination, if source doesnt exisit in parent.children, if destination doesnt exit in parent.children, return False
            return False
        comp = src_parent.get(src_name)                     #Grab the component file or direct obj from its current parent directory
        src_parent.remove(src_name)                         #Remove the same component from the source parents childrebn map
        comp.name = dst_name                                #Rename the Component to its new name (the last segment of the destination path)
        dst_parent.add(comp)                                # Insert the now-renamed Component into the destination parent’s children map
        return True                                         #if successful return True

    def list_dir(self, path: str) -> List[str]:
        if path == "/":
            return self.root.list_children()     #If the caller asks to list /, we simply delegate to the root directory’s list_children() method, which returns a flat list of the names of its immediate children.
        parent, name = self._traverse(path)
        if not parent:      #We use our _traverse helper to walk down the tree and find the parent Directory object plus the final component name. If traversal failed (invalid path, non-directory in the way, etc.), we return an empty list.
            return []
        comp = parent.get(name)     #We look up the component named name under parent.
        if comp and comp.is_directory():
            return comp.list_children()     #If it exists and is a directory, we again call its list_children() to get the names of its immediate child files/directories.
        return []

    def search(self, name: str) -> List[str]:
        """
        Recursively search from root for any component with the given name.
        Returns full paths.
        """
        results = []

        def dfs(dir_node: Directory, prefix: str):
            for child in dir_node.children.values():            #For each child, Build its full path (child_path) by appending its name to prefix.
                child_path = prefix + (child.name if prefix.endswith("/") else "/" + child.name)
                if child.name == name:                  # if child.name equals the search target, add child_path to results.
                    results.append(child_path)
                if child.is_directory():                #: if the child is a directory, call dfs(...) on it, extending the prefix appropriately (ensuring it ends in /
                    dfs(child, child_path if child_path.endswith("/") else child_path + "/")

        dfs(self.root, "/")        #Kick off from the root 
        return results              #Found all the paths

