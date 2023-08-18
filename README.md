# HDict
A dictionary implementation that allows for hashing


## Usage

```python
from io import StringIO
from hdict import HDict

example = HDict("one", 1, 2, "two", three=3, four=4, values={"five": 5}, factory=list)

expected_json = """{
    "three": 3,
    "four": 4,
    "one": 1,
    "2": "two",
    "five": 5
}"""

assert "one" in example
assert 2 in example
assert "three" in example
assert "five" in example
assert example[2] == "two"
assert "list" not in example
assert example['list'] == list()
assert example["five"] == 5
assert not example.empty
assert example.dumps() == expected_json

buffer = StringIO()
example.write(buffer)
buffer.seek(0)

assert buffer.read() == expected_json
assert HDict.loads('{"one": 1, "two": 2}') == HDict(one=1, two=2)
```