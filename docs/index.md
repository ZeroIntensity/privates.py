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
    __readonly__ = "bar",

    def __init__(self):
        self.bar = "hello world!"

hello = Hello()
print(hello.bar)  # hello world!
hello.bar = "goodbye, world :("  # AccessError
```

## License

`privates.py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
