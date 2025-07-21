# Clarifying questions

#LRU Cache (Least Recent Used) - Distributed
# Primarily i know is it is used for frequently accessed data, to make read and write fast
#user insert the data and retrieve the data

#Support get and put operations? yes
#should both be in O(1) time ? yes
#Cache have a fixed capacity ? yes
#Thinking of using hashmap
#Put : key value : integers or generic-> int
#Get: key , key if non existenet return -1
#Should I update the value if the key already exists? yes
#Thread safety? yes
#is 0 or negatives allowed? no

#Beacuse it is a distrivuted system, and for thread safety, i will use  coarse grained lock on the cache

#I plan to use a combination of a HashMap and a Doubly Linked List
#HashMap: cause it has both key and value pair, map keys → nodes (O(1) access)
#Doubly linked list to track usage order, with most recently used at head, least recently used at tail.
#Put operation: if key exists → fetch node from hashmap and update its value, remove it from current position in DLL, and move to head
# if key doesnt exist: create a new node, -> capacity of LLD , not full, add new node to head, and key, node mapping in hashmap
# new node, over capacity, remove tail node(LRU), remove its key from Hashmap, then insert new node at head, key node mapping in hashmap
# get () - key exists in hashmap -> fetch node from hashmap and update its value, remove it from current position in DLL, and move to head
# doesnt exist return -1

"""✅ LRU Cache System Design Verbal Explanation (Refined)
"Before diving into implementation, I'd like to clarify the core functionality and walk through my planned design for the LRU (Least Recently Used) Cache.

🔍 Clarifications
- The cache should support get(key) and put(key, value) operations in O(1) time.
- It has a fixed capacity. If that capacity is exceeded, we evict the least recently used item.
- For get(key), if the key doesn't exist, we return -1.
- For put(key, value), if the key already exists, we update the value and treat it as most recently used.
- Thread safety is a requirement, so I will ensure synchronization around shared structures.

💡 Design Plan
To achieve constant time operations and track usage order, I will use a combination of:
- A HashMap to map keys to nodes.
- A Doubly Linked List to maintain the usage order (head = MRU, tail = LRU).
This structure allows:
- O(1) access to nodes via the HashMap
- O(1) insert/remove operations in the doubly linked list

🧩 PUT Operation:
If the key already exists:
- Fetch the node from the map
- Update its value
- Move the node to the head (most recently used)
If the key does not exist:
-If capacity is full:
    Remove the tail node (least recently used)
    Remove its key from the map
    Create a new node
    Add it to the head of the DLL
    Add the key-node mapping to the map

🧩 GET Operation:
If the key exists:
- Retrieve the node from the map
- Move it to the head of the DLL
- Return the node's value
If the key doesn't exist:
- Return -1

🔒 Thread Safety
To handle concurrent access,I will wrap the get() and put() operations using a lock (e.g., threading.Lock() in Python) to synchronize access to the shared map and list.

📌 Final Note
If this plan aligns with the expectations, I will proceed with the implementation using a simple Node class for the doubly linked list, a HashMap for key-node mapping, and a LRUCache class managing the entire logic."""

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

#import threading
       
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {} #hashmap : key value pairs
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        #self.lock = threading.Lock()  # For thread safety
        
    def get(self, key):
      #with self.lock:
        if key in self.cache:
            node = self.cache[key]
            self.move_to_head(node)
            return node.value
        return -1
    
    def put(self, key, value):
      #with self.lock:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.move_to_head(node)
        else:
            node = Node(key, value)
            self.cache[key] = node
            self.add_to_head(node)
            if len(self.cache)> self.capacity:
                removed_node = self.remove_tail()
                del self.cache[removed_node.key]
       
         
    def remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        
    def add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def move_to_head(self, node):
        self.remove_node(node)
        self.add_to_head(node)
    
    def remove_tail(self):
        node = self.tail.prev
        self.remove_node(node)
        return node
        
        
#If with locking: just add the # statements in the logic nothing else!!