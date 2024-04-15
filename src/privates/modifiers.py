from __future__ import annotations

import functools
from types import FrameType, FunctionType
from typing import Any, Callable, Iterable, TypeVar, Union

from typing_extensions import ParamSpec

from ._util import get_back_frame
from .exceptions import AccessError

__all__ = (
    "supports_private",
    "class_modifier",
    "function_modifier",
    "private",
    "friend",
)

T = TypeVar("T")
P = ParamSpec("P")


def _check_access(
    co_name: str,
    tp: type | FunctionType,
    frame: FrameType,
) -> bool:
    if isinstance(tp, FunctionType) and (tp.__code__ == frame.f_code):
        return True

    attr = getattr(tp, co_name, None)
    if isinstance(attr, property):
        for prop_func in (attr.fget, attr.fdel, attr.fset):
            if isinstance(prop_func, FunctionType):
                if prop_func.__code__ == frame.f_code:
                    return True

    if isinstance(attr, FunctionType):
        if attr.__code__ == frame.f_code:
            return True

    return False


def _ensure_access(
    protected: Iterable[str],
    privates: Iterable[str],
    readonly: Iterable[str],
    subclasses: set[type],
    friends: set[type | FunctionType],
    tp: type,
    name: str,
) -> None:
    if (name in protected) or (name in readonly):
        frame = get_back_frame()
        co_name = frame.f_code.co_name

        for subclass in subclasses:
            if _check_access(co_name, subclass, frame):
                return

        for friend in friends:
            if _check_access(co_name, friend, frame):
                return

        msg = "protected" if name in protected else "read-only"
        raise AccessError(
            f"attempted to access {msg} attribute {name!r} outside of subclass to {tp.__name__}"  # noqa
        )

    if (name.startswith("_") and (not name.endswith("__"))) or (
        name in privates
    ):
        frame = get_back_frame()
        co_name = frame.f_code.co_name

        if _check_access(co_name, tp, frame):
            return

        for friend in friends:
            if _check_access(co_name, friend, frame):
                return

        raise AccessError(
            f"attempted to access private attribute {name!r} outside of class {tp.__name__}"  # noqa
        )


def supports_private(tp: type[T]) -> type[T]:
    """Enable checking of attributes on the target type.

    Args:
        tp: Type to enable checking on.
    """
    old_getattribute = tp.__getattribute__
    old_setattribute = tp.__setattr__
    old_delattribute = tp.__delattr__
    tp.__friends__ = set()  # type: ignore
    privates: Iterable[str] = getattr(tp, "__private__", set())
    protected: Iterable[str] = getattr(tp, "__protected__", set())
    readonly: Iterable[str] = getattr(tp, "__readonly__", set())
    old_init_subclass = tp.__init_subclass__
    subclasses: set[type] = {tp}
    friends: set[type | FunctionType] = tp.__friends__  # type: ignore

    def subclass_wrapper(cls, *args, **kwargs) -> None:
        subclasses.add(cls)
        old_init_subclass(*args, **kwargs)  # type: ignore

    tp.__init_subclass__ = classmethod(subclass_wrapper)  # type: ignore

    def get_wrapper(self, name: str) -> Any:
        if name in readonly:
            # public get access for readonly attributes
            return old_getattribute(self, name)  # type: ignore

        _ensure_access(
            protected,
            privates,
            set(),
            subclasses,
            friends,
            tp,
            name,
        )
        return old_getattribute(self, name)  # type: ignore

    def set_wrapper(self, name: str, value: Any) -> Any:
        _ensure_access(
            protected,
            privates,
            readonly,
            subclasses,
            friends,
            tp,
            name,
        )
        return old_setattribute(self, name, value)  # type: ignore

    def del_wrapper(self, name: str) -> None:
        _ensure_access(
            protected,
            privates,
            readonly,
            subclasses,
            friends,
            tp,
            name,
        )
        return old_delattribute(self, name)  # type: ignore

    tp.__getattribute__ = get_wrapper  # type: ignore
    tp.__setattr__ = set_wrapper  # type: ignore
    tp.__delattr__ = del_wrapper  # type: ignore

    return tp


def class_modifier(
    target: type[T],
) -> type[T]:
    """Modify the access rules for a class.

    Example:
        ```py
        from privates import access_modifier

        @class_modifier()
        class Hello:
            ...

        # Hello is now only usable in this module!
        ```"""
    frame = get_back_frame()

    if not isinstance(target, type):
        raise TypeError(
            "class_modifier() can only be applied to classes. use function_modifier() instead"  # noqa
        )
    supports_private(target)
    friends: set[type | FunctionType] = target.__friends__  # type: ignore

    init = target.__init__

    def inner(*args: Any, **kwargs: Any) -> None:
        caller_frame = get_back_frame()
        if caller_frame.f_locals != frame.f_locals:
            ok: bool = False

            for friend in friends:
                if isinstance(friend, type):
                    for attr_name in dir(friend):
                        func = getattr(friend, attr_name)

                        if not isinstance(func, FunctionType):
                            continue

                        if func.__code__ == caller_frame.f_code:
                            ok = True
                            break
                elif friend.__code__ == caller_frame.f_code:
                    ok = True
                    break

            if not ok:
                raise AccessError(
                    f"attempted to access {target} outside of it's scope"
                )

        init(*args, **kwargs)

    target.__init__ = inner  # type: ignore
    return target


def function_modifier(
    func: Callable[P, T],
) -> Callable[P, T]:
    """Apply a private modifier to a function."""
    frame = get_back_frame()

    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        caller_frame = get_back_frame()

        if caller_frame.f_locals != frame.f_locals:
            raise AccessError(
                f"attempted to access private {func} from outside it's scope"
            )

        return func(*args, **kwargs)

    return inner


A = TypeVar("A", bound=Union[type, Callable])


def private(
    func_or_type: A,
) -> A:
    """Apply `class_modifier` if the object is a class, otherwise apply `function_modifier`."""  # noqa
    if isinstance(func_or_type, type):
        return class_modifier(func_or_type)  # type: ignore
    else:
        if not callable(func_or_type):
            raise TypeError(f"expected a callable, got {func_or_type}")
        return function_modifier(func_or_type)  # type: ignore


def friend(
    tp: type[Any],
) -> Callable[[A], A]:
    """Allow the type or function to touch private attributes of the type."""
    friends = getattr(tp, "__friends__", None)

    if friends is None:
        raise TypeError(
            f"{tp} does not support private attributes, so friend() is useless"
        )

    def inner(new_friend: A) -> A:
        friends.add(new_friend)
        return new_friend

    return inner
