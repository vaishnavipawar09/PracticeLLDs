"""
Important Things to remember 

An enum (short for “enumeration”) is a special data type that lets you define a fixed set of named constants. 

Instead of scattering raw values (like 1, 2, "RED", "GREEN") throughout your code, you group them under a single type:
Why use enums?
Readability & Maintainability
    You refer to Signal.RED instead of 1 or "RED", making the intent clear.
Type Safety
    Enums prevent invalid values at runtime (e.g. you can’t accidentally use Signal.PURPLE).
Namespace Organization
    All related constants live in one place, avoiding “magic strings/numbers” scattered in your code.
Iteration & Comparison
    You can loop over Signal members (for s in Signal: …) and rely on identity (if light == Signal.GREEN:) rather than loose string comparisons.

@classmethod vs. @staticmethod
@classmethod
Receives the class (cls) as the first argument.
Can access or modify class state.
Used here for get_instance(cls) so we can return the singleton via the class, without needing an existing instance.

@staticmethod
Does not receive self or cls.
Behaves like a plain function scoped inside the class.
Cannot modify object or class state.
Useful for utility methods that logically belong to the class but don’t need its state.

Why Lock?
Thread safety: multiple threads could call TrafficController() at the same time.
Double-checked locking: we first check if _instance is None outside the lock (fast path), then acquire the lock and check again before creating the instance.
Lock purpose: prevents two threads from both observing _instance as None and each creating a separate controller.


__name__ and if __name__ == "__main__":
__name__
Every Python module gets a built-in variable __name__.

If you run the file directly (e.g. python traffic.py), then inside that file __name__ == "__main__".

If you import it from somewhere else (import traffic), then __name__ is set to the module’s name ("traffic").

if __name__ == "__main__":
This guard means “only execute the following code when this file is run as a script, not when it’s imported.”
It’s how you put your demo or test harness in a module without it firing on import.

__new__
Purpose
__new__ is the constructor that actually creates (allocates) the new instance.
It’s called before __init__.


__init__
Purpose
__init__ is the initializer—it runs after the instance is created, to set up its attributes.

Singleton gotcha
Even if __new__ returns the same object repeatedly, __init__ will still run every time you call Singleton().
If you need one-time setup only, guard your __init__ logic:

_instance (class variable)
Role in singleton
It holds the one and only object created.

First time you call the class, _instance is None, so you allocate a new object and store it there.

Subsequent calls return whatever’s in _instance.

Why a class variable?
Because you want it shared across all calls to __new__, regardless of which reference to the class you use.

str.zfill(width) is a built-in Python string method that pads the string on the left with ASCII '0' characters until it reaches the specified total width.


"""