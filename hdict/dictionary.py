"""
Defines the core hashable dictionary
"""
from __future__ import annotations

import typing
import json

_KT = typing.TypeVar("_KT", bound=typing.Hashable)
"""A generic type representing a key. Must be hashable."""

_VT = typing.TypeVar("_VT", bound=typing.Hashable)
"""A generic type representing a value. Must be hashable"""


def _parameters_are_key_value_pairs(*args) -> bool:
    """
    Check if the passed in positional arguments are in the form of 
    [[key, value], [key, value], [key, value]]
    """
    if len(args) == 0:
        return False

    for arg in args:
        if not (isinstance(arg, typing.Sequence) and len(arg) == 2):
            return False
        if not isinstance(arg[0], typing.Hashable):
            return False
        if not isinstance(arg[1], typing.Hashable):
            return False
    return True

def _parameters_is_key_value_list(*args) -> bool:
    """
    Check to see if the passed in positional arguments are in the form of 
    [key, value, key, value, key, value]
    """
    if len(args) == 0:
        return False

    if len(args) % 2 != 0:
        return False

    unhashable_keys = [
        args[index]
        for index in range(0, len(args), 2)
        if not isinstance(args[index], typing.Hashable)
    ]

    return len(unhashable_keys) == 0


class HDict(typing.Dict[_KT, _VT]):
    """
    A dictionary that may be hashed
    """
    @classmethod
    def loads(cls, string: str, **kwargs) -> HDict:
        """
        Convert a json string to a hashable dictionary

        Args:
            string: The string to attempt to convert into a hashable dictionary

        Returns:
            A hashable dictionary
        """
        loaded_dictionary = json.loads(string, **kwargs)
        return cls(**loaded_dictionary)

    def __init__(
        self,
        *args,
        values: typing.Mapping[_KT, _VT] = None,
        factory: typing.Callable[[], _VT] = None,
        **kwargs
    ):
        """
        Constructor

        Args:
            args: Positional arguments defining key value pairs
            values: A mapping of preexisting values to add to the dictionary
            factory: An optional function used to create missing items on retrieval
            kwargs: keyword arguments that will be added to the dictionary
        """
        if _parameters_are_key_value_pairs(*args):
            for key, value in args:
                kwargs[key] = value
        elif _parameters_is_key_value_list(*args):
            for value_index in range(1, len(args), 2):
                kwargs[args[value_index - 1]] = args[value_index]
        elif len(args) == 1 and isinstance(args[0], typing.Mapping):
            kwargs.update(args[0])
        elif args:
            raise ValueError(
                "An even number of arguments must be passed if keys and values are " +
                f"to be passed into a {self.__class__.__name__} individually"
            )

        super().__init__()
        self.__factory = factory

        for key, value in kwargs.items():
            self[key] = value

        if isinstance(values, typing.Mapping):
            for key, value in values.items():
                self[key] = value

    def __setitem__(
        self,
        key: typing.Union[typing.Hashable, typing.Mapping],
        value: typing.Union[typing.Hashable, typing.Mapping]
    ):
        """
        Assign the given value to the given key.

        Passed unhashable maps will be attempted to be converted to a hashable map

        Args:
            key: The key for the value. Must be hashable or a map
            value: A value to assign to the key. Must be hashable or a map
        """
        if isinstance(key, typing.Mapping) and not isinstance(key, typing.Hashable):
            key = self.__class__(values=key)

        if isinstance(value, typing.Mapping) and not isinstance(value, typing.Hashable):
            value = self.__class__(values=value)
        elif not isinstance(value, typing.Hashable):
            raise ValueError(
                f"An item cannot be inserted into a {self.__class__.__name__} - " + \
                "the value is not hashable"
            )
        elif not isinstance(key, typing.Hashable):
            raise ValueError(
                f"An item cannot be inserted into a {self.__class__.__name__} - " + \
                "the key is not hashable"
            )
        super().__setitem__(key, value)

    def __getitem__(self, __key: _KT) -> _VT:
        """
        Get the value assigned to the key. If there is a factory and a value has not 
        been assigned to the key yet, a new item will be created for that key.
        """
        if __key not in self and isinstance(self.__factory, typing.Callable):
            self[__key] = self.__factory()

        return super().__getitem__(__key)

    def __hash__(self):
        return hash(frozenset(self))

    @property
    def empty(self) -> bool:
        """
        Whether the dictionary is empty
        """
        return len(self) == 0

    def to_json(self, **kwargs) -> str:
        """
        Convert the dictionary to a JSON string
        """
        if "indent" not in kwargs:
            kwargs['indent'] = 4
        return json.dumps(self, **kwargs)

    def write(self, path_or_buffer: typing.Union[str, typing.IO[str]], *args, **kwargs):
        """
        Write this dictionary to a buffer as json data
        """
        if "indent" not in kwargs:
            kwargs['indent'] = 4
        json.dump(self, path_or_buffer, *args, **kwargs)
