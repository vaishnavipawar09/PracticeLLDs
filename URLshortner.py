#Clarifying Questions:

#Users submit long url to short ? yes
#support vice versa, give short get long? yes
#shortening process will it generate new url every time? yes it is unique
#use base62-encoded ID as the short url suffix? yes (a-z, A-Z 0-9)
#url is case sensitive? yes
#shortened striing of fixed length ? yes 6 characters
#short URLs be globally unique ? yes
#Should we check for duplicate long URLs and avoid inserting them again? no
#storing everything in memory for now? or db? - for now inmemory (dictonary/hashmap)
#Do URLs expire after some time? no for now
#need a thread safe operations? yes on ID counter for now


#Base62 encoding: performs encode and decode
#URLstore: 
#URL shortener service (main class) shorten and expand

# ✅ Verbal Design Pitch: URL Shortener
# We are designing a basic URL shortening system that allows users to:
# - Submit a long URL and receive a globally unique 6-character short string
# - Retrieve the original long URL using the short string
# 
# Core Requirements:
# - Generate new short URL each time (no duplicate long URL check)
# - Short string is case-sensitive, Base62-encoded (0-9, a-z, A-Z)
# - Fixed-length 6-character short strings
# - Thread-safe ID generation for unique short URLs
# - All data is stored in memory using dictionaries
# 
# System supports:
# - One-way shortening (Long ➝ Short)
# - Reverse lookup (Short ➝ Long)
# 
# We will implement three classes:
# 1. Base62Encoder – Utility for encoding/decoding integer IDs to Base62 strings
# 2. URLStore – Thread-safe in-memory storage for mappings and ID generation
# 3. URLShortenerService – Main class that handles shortening and expanding logic
# 
# If this structure meets the requirements, we will proceed to implement and test each class.


class Base62Encoder:
    """
    Utility class to encode a unique integer ID to a Base62 string.
    Base62 uses [0-9][a-z][A-Z] – total 62 characters.
    """
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = 62
    
    @staticmethod
    def encode(num):                                    #turns integer 1001 into something like 'G7e2xA'.
        if num == 0:
            return Base62Encoder.characters[0]
        
        result = []
        while num > 0:
            remainder = num % Base62Encoder.base  #gives a digit in base 62, maps it to corresponding character
            result.append(Base62Encoder.characters[remainder]) # append the remainder to the result
            num = num // Base62Encoder.base         #Divide again by 62 and repeat
        return ''.join(reversed(result)).zfill(6)   #Always return 6 char string
            
            #num = 125     125 % 62 == 1 _> '1  125 // 62 = 2
            # 2 %  62 - 2 _> '2' result = [1, 2] reverse becomes 21  
            
    @staticmethod
    def decode(encode_str):                             #turns 'G7e2xA' back into 1001
        num = 0
        for char in encode_str:
            num = num * Base62Encoder.base + Base62Encoder.characters.index(char)
        return num
    
    #encoded str = 000021           0 *62 + 0 = 0 x 4, 0x62 +2 = 2, 2x62 + 1 = 125
    
import threading
class URLStore:
    """
    Handles in-memory storage of short and long URLs.
    Uses a thread-safe mechanism to ensure consistent updates.
    """
    
    def __init__(self):
        self.id_counter = 0
        self.lock = threading.Lock()
        self.id_to_url = {}
        self.short_to_url = {}
        
    def store(self, long_url):
        with self.lock :
            self.id_counter += 1
            unique_id = self.id_counter
            self.id_to_url[unique_id] = long_url
        return unique_id

    def get_by_id(self, unique_id):                 #decoding the short string → back to long URL.
        return self.id_to_url.get(unique_id)
    
    def map_short_to_url(self, short_string, long_url):     #Map Short URL → Long URL
        self.short_to_url[short_string] = long_url
            
    def get_by_short(self, short_string):           #Get by Short URL
        return self.short_to_url.get(short_string)
            

class URLShortnerService:
    def __init__(self):
        self.store = URLStore()
        
    def shorten(self, long_url):                    #long url to short str
        unique_id = self.store.store(long_url)
        short_str = Base62Encoder.encode(unique_id)
        self.store.map_short_to_url(short_str, long_url)
        return short_str
    
    def expand(self, short_url):
        return self.store.get_by_short(short_url)