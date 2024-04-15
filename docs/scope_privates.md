# Limiting to a scope

privates.py provides three functions for limiting an object to it's own scope: `class_modifier`, `function_modifier`, and `private`. As you might have guessed, `class_modifier` is only for classes, `function_modifier` is only for functions, and `private` will decide what to use based on the object you give it. For example:

```py
from privates import class_modifier, function_modifier

@class_modifier
class Hello:
    ...

@function_modifier
def hello():
    ...

# Hello and hello can not be used outside of this module!
```


!!! tip

    While `class_modifier` and `function_modifier` are part of the public API, they are a bit more low level as opposed to `private`. You should try to use `private` wherever possible.

## Scope vs Module

privates.py limits objects to their *scope* (as in, their locals), meaning that private objects in their own file might not be able to access each other. See the example below:

```py
from privates import private

def inner():
    @private
    class A:
        ...

    A()  # Works just fine
    return A

A = inner()
A()  # AccessError
```

Note that if an object is in the global scope (as with the examples above), then it *is* the same as locking an object to its module. This is simply because the `locals` and `globals` are equivalent in this case.

## Semantics

`private`, `class_modifier`, and `function_modifier` don't prevent referencing private functions or types, only *calling* them. You may still access static or class attributes on types:

```py
from privates import private

@private
class Test:
    @classmethod
    def do_something(cls):
        ...

# Test.do_something() is NOT locked, but creating a new instance of Test is
```

## Friends

You may give a function or type private access with the `friend` decorator:

```py
from privates import friend, private

def inner():
    @private
    class A:
        def __init__(self, value: int) -> None:
            self.value = value

    return A

A_locked = inner()

@friend(A_locked)
def use_a():
    a = A_locked(42)
    print(a.value)

use_a()
```
