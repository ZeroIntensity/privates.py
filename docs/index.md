# Welcome to the privates.py documentation!

## Stop others from touching your privates!

- [PyPI](https://pypi.org/project/privates.py)
- [Source](https://github.com/ZeroIntensity/privates.py)

## Installation

### Linux/macOS


```console
python3 -m pip install -U privates.py
```

### Windows


```console
py -3 -m pip install -U privates.py
```

## Example

```py
from privates import private

@private
class Hello:
    ...

# Hello is now only accessible in this module!
```
