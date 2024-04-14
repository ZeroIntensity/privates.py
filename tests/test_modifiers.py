from pytest import raises

from privates import (
    AccessError,
    class_modifier,
    friend,
    function_modifier,
    private,
    supports_private,
)


def test_class_modifier():
    def inner():
        @class_modifier
        class Test:
            def __init__(self, value: int) -> None:
                self.value = value

        t = Test(2)
        assert t.value == 2
        return Test

    Test = inner()
    with raises(AccessError):
        Test(2)

    with raises(TypeError):

        @class_modifier  # type: ignore
        def hello(): ...


def test_function_modifier():
    def inner():
        @function_modifier
        def hello(a: int):
            return a + 1

        assert hello(1) == 2
        return hello

    hello = inner()
    with raises(AccessError):
        hello(1)


def test_private():
    def a():
        @private
        class A:
            def __init__(self):
                self.value = 1

        assert A().value == 1
        return A

    def b():
        @private
        def func_b():
            return 1

        assert func_b() == 1
        return func_b

    A = a()
    func_b = b()

    with raises(AccessError):
        A()

    with raises(AccessError):
        func_b()

    with raises(TypeError):
        private(10)  # type: ignore


def test_private_protocol():
    @supports_private
    class A:
        def __init__(self, value: int):
            self._value = value

        @property
        def value(self) -> int:
            return self._value

        def something(self):
            self._value += 1

    a = A(1)
    with raises(AccessError):
        a._value

    assert a.value == 1
    a.something()
    assert a.value == 2

    with raises(AccessError):
        del a._value


def test_protected_protocol():
    @supports_private
    class A:
        __protected__ = ("value",)

        def __init__(self, value: int):
            self.value = value

        @property
        def thing(self) -> int:
            return self.value

    class Hello(A):
        def __init__(self):
            super().__init__(1)

        @property
        def something(self) -> int:
            return self.value

    a = A(42)

    with raises(AccessError):
        a.value

    assert a.thing == 42

    hello = Hello()
    assert hello.something == 1

    with raises(AccessError):
        hello.value


def test_friends():
    @supports_private
    class A:
        def __init__(self, value: int):
            self._value = value

    @friend(A)
    class B:
        def __init__(self):
            self.a = A(42)

        @property
        def value(self) -> int:
            return self.a._value

    b = B()
    assert b.value == 42

    @friend(A)
    def test():
        a = A(10)
        assert a._value == 10

    test()

    class C: ...

    with raises(TypeError):

        @friend(C)
        def foo(): ...


def test_readonly():
    @supports_private
    class A:
        __readonly__ = ("value",)

        def __init__(self, value: int) -> None:
            self.value = value

    a = A(10)
    assert a.value == 10

    with raises(AccessError):
        a.value = 42

    with raises(AccessError):
        del a.value

    @friend(A)
    def test():
        a.value = 42

    test()
    assert a.value == 42
