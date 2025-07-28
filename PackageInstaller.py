# 🔍 Clarifying Questions:
# 1. Package Model:
#    – What metadata does each package have? (e.g., name, version, list of dependency names)
# 2. Repository:
#    – Where do we fetch packages from? (assume a simple in-memory repository for now)
# 3. Versions:
#    – Do we need to handle multiple versions or just one “latest” per package?
# 4. Operations:
#    – Must support install(name), uninstall(name), list_installed()
#    – Should uninstall cascade and remove unused dependencies?
# 5. Dependency Semantics:
#    – If A depends on B, install(B) first. Detect and error on cycles.
# 6. Persistence:
#    – Is installed-state persisted across runs? (we’ll keep an in-memory set)
# 7. Concurrency:
#    – Will multiple installs run in parallel? (assume single‐threaded CLI)

# ✅ Verbal Design Pitch:
# We’re building a simple package installer that:
#  • Knows about available packages (Repository)
#  • Resolves dependencies via topological sort (DependencyResolver) 
"""
We do this by building a directed graph of “A → B” edges and performing a topological sort. 
That both (a) guarantees you install in the correct order and (b) detects cycles (so you don’t try to install things that depend on each other forever).
"""
#  • Installs in correct order (Installer)
#  • Tracks installed packages (PackageManager facade)
"""
In the LLD we just walked through:

Repository holds the metadata for “what packages exist and what they depend on.”
DependencyResolver runs a DFS to gather all needed packages, then Topological sort to produce a valid install sequence or throw a cycle error.
Installer runs the per-package “install” or “uninstall” steps.
PackageManager is our façade (and singleton) that ties it all together: you call pm.install("MyApp"), it resolves, installs in the right order, skips already-installed items, and keeps track of the final state.
This is essentially what apt, yum, pip, npm, or brew do in the wild—just with a lot more edge-cases (version constraints, remote fetching, transaction rollbacks, caching, etc.).
"""
# Core Classes:
# 1. Package              — holds name, version, dependencies
# 2. Repository           — in-memory store of available Package objects
# 3. DependencyResolver   — detects cycles, returns install order
# 4. Installer            — applies installation logic per package
# 5. PackageManager       — singleton facade exposing install/uninstall/list

from collections import deque, defaultdict
from typing import List, Dict, Set

class DependencyError(Exception):               # built-in Exception class to create our own custom exception type.
    pass

class CircularDependencyError(DependencyError):
    pass

class PackageNotFoundError(DependencyError):
    pass

class Package:
    """Represents a software package with dependencies."""
    def __init__(self, name: str, version: str, dependencies: List[str]):
        self.name = name
        self.version = version
        self.dependencies = dependencies

class Repository:
    """In-memory store of all available packages."""
    def __init__(self):
        self.packages: Dict[str, Package] = {}

    def add_package(self, pkg: Package):
        self.packages[pkg.name] = pkg

    def get(self, name: str) -> Package:
        pkg = self.packages.get(name)
        if not pkg:
            raise PackageNotFoundError(f"Package '{name}' not found in repository")
        return pkg

class DependencyResolver:
    """Builds dependency graph and returns a topological install order."""
    def __init__(self, repo: Repository):
        self.repo = repo

    def resolve(self, root: str) -> List[Package]:      #We’re defining resolve(root) to compute a topological ordering of packages starting from root.
        # Build graph of name -> set(dependencies)
        graph: Dict[str, Set[str]] = {}                 #graph will map each package name to the set of names it depends on.
        visited: Set[str] = set()                       #visited tracks which package names we’ve already traversed, to avoid infinite recursion.

        def dfs_build(pkg_name: str):                   #dfs_build is a helper to traverse the dependency tree.
            if pkg_name in visited:                     #If we’ve already seen pkg_name, we stop.
                return
            visited.add(pkg_name)                       #Otherwise we mark it visited, fetch the Package object from the repository, record its dependency list in graph, 
            pkg = self.repo.get(pkg_name)
            graph[pkg_name] = set(pkg.dependencies)
            for dep in pkg.dependencies:                #and recurse into each dependency.
                dfs_build(dep)

        dfs_build(root)                                 #Kick off the DFS from the requested root package name.

        # Kahn's algorithm for topological sort
        indegree = defaultdict(int)                     #indegree counts how many incoming edges each node has. First we ensure every package appears in indegree (even if zero
        for pkg, deps in graph.items():                 #Then for each dependency edge pkg → dep, we increment indegree[dep].
            indegree[pkg]  # ensure key exists
            for dep in deps:
                indegree[dep] += 1

        queue = deque([n for n, d in indegree.items() if d == 0])       #Initialize a queue of all nodes with zero in-degree (i.e., no uninstalled prerequisites).
        order: List[str] = []                                           #order will collect the sorted package names.

        while queue:
            node = queue.popleft()                  #Repeatedly remove a “ready” node from the queue, append to order, then decrement the in-degree of its dependents.
            order.append(node)
            for nbr in graph.get(node, []):
                indegree[nbr] -= 1
                if indegree[nbr] == 0:              #Any dependent whose in-degree drops to zero is now ready and gets enqueued.
                    queue.append(nbr)

        if len(order) != len(graph):                #If we didn’t process every node, there must be a cycle. We throw our custom CircularDependencyError.
            raise CircularDependencyError("Cycle detected among: " +
                                          ", ".join(graph.keys()))
        # Map names back to Package objects
        return [self.repo.get(name) for name in order]      #Finally, convert the list of package names back into the actual Package objects in sorted order.

class Installer:
    """Handles the actual installation steps."""
    def install(self, pkg: Package):
        # In real life: download, verify checksum, unpack, etc.     #Installer encapsulates how to perform the install/uninstall. Right now it just prints—but you could plug in real I/O here.
        print(f"Installing {pkg.name}-{pkg.version}...")

    def uninstall(self, pkg: Package):
        print(f"Uninstalling {pkg.name}-{pkg.version}...")

class PackageManager:
    """Singleton facade: install, uninstall, list. : only one instance is ever created."""
    _instance = None

    def __new__(cls, repo: Repository):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(repo)
        return cls._instance

    def _init(self, repo: Repository):          #The first time you call PackageManager(repo), we allocate and initialize; subsequent calls return the same instance.
        self.repo = repo                                #The Repository
        self.resolver = DependencyResolver(repo)        #A DependencyResolver (to compute install order)
        self.installer = Installer()                    #An Installer (to actually do installs)
        self.installed: Dict[str, Package] = {}         #A map of already-installed packages.

    def install(self, name: str):                   #install(name) first asks the resolver for a dependency-sorted list.
        # Resolve dependencies in order
        install_list = self.resolver.resolve(name)
        for pkg in install_list:                    #It then walks that list, installing any package not yet installed and recording it.
            if pkg.name not in self.installed:
                self.installer.install(pkg)
                self.installed[pkg.name] = pkg
            else:
                print(f"{pkg.name} already installed, skipping")

    def uninstall(self, name: str):             #uninstall(name) only uninstalls if it’s currently installed.
        pkg = self.installed.get(name)
        if not pkg:
            print(f"{name} is not installed")
            return
        # In a real system we’d check reverse-deps; here we just uninstall
        self.installer.uninstall(pkg)
        del self.installed[name]

    def list_installed(self):               #list_installed() simply enumerates everything in the installed map.
        print("Installed packages:")
        for pkg in self.installed.values():
            print(f" - {pkg.name}-{pkg.version}")

# -------------------
# Example Usage:
# -------------------
if __name__ == "__main__":
    repo = Repository()
    # Define some sample packages
    repo.add_package(Package("A", "1.0", ["B", "C"]))
    repo.add_package(Package("B", "1.1", ["C"]))
    repo.add_package(Package("C", "2.0", []))
    repo.add_package(Package("D", "3.0", ["A", "E"]))
    repo.add_package(Package("E", "1.2", []))

    pm = PackageManager(repo)
    pm.install("D")
    pm.list_installed()
    print()
    pm.uninstall("B")
    pm.list_installed()

"""
 We build a Repository of packages A, B, C, D, E with a simple dependency graph.
We get our singleton PackageManager, ask it to install D (which pulls in E, C, B, A in the correct order), then list what got installed.
Then we attempt to uninstall B and list again.
That’s the full flow—from building the dependency graph, detecting cycles, ordering installs, applying them, and managing your installed-package state.
        """