# Limiting to a scope

privates.py provides three functions for limiting an object to it's own scope: `class_modifier`, `function_modifier`, and `private`. As you might have guessed, `class_modifier` is only for classes, `function_modifier` is only for functions, and `private` will decide what to use based on the object you give it.


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
