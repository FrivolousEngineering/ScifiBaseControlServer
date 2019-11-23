# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) Thiago Marcos P. Santos
# Copyright (c) Christopher S. Case
# Copyright (c) David H. Bronke
# This file is released under LGPL.

import inspect
import threading
import weakref
from typing import List, Any, Tuple, Union, Callable, Generic, Iterable, Optional, TypeVar, cast
from weakref import ReferenceType


class Signal:
    """
    Simple implementation of signals and slots.

    Signals and slots can be used as a light weight event system. A class can
    define signals that other classes can connect functions or methods to, called slots.
    Whenever the signal is called, it will proceed to call the connected slots.

    To create a signal, create an instance variable of type Signal. Other objects can then
    use that variable's `connect()` method to connect methods, callable objects or signals
    to the signal. To emit the signal, call `emit()` on the signal. Arguments can be passed
    along to the signal, but slots will be required to handle them. When connecting signals
    to other signals, the connected signal will be emitted whenever the signal is emitted.

    Signal-slot connections are weak references and as such will not prevent objects
    from being destroyed. In addition, all slots will be implicitly disconnected when
    the signal is destroyed.

    \warning It is imperative that the signals are created as instance variables, otherwise
    emitting signals will get confused. To help with this, see the SignalEmitter class.

    Loosely based on http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/
    \sa SignalEmitter
    """
    def __init__(self, **kwargs) -> None:
        """
        Create a signal. A signal can be fired by calling .emit.
        :param kwargs:
        """
        # These collections must be treated as immutable otherwise we lose thread safety.
        self.__functions = WeakImmutableList()  # type: WeakImmutableList[Callable[[], None]]
        self.__methods = WeakImmutablePairList()  # type: WeakImmutablePairList[Any, Callable[[], None]]
        self.__signals = WeakImmutableList()  # type: WeakImmutableList[Signal]

        self.__lock = threading.Lock()  # Guards access to the fields above.

    def __call__(self):
        raise NotImplementedError("Call emit() to emit a signal")

    def emit(self, *args, **kwargs) -> None:
        """
        Emit the signal which directly calls all of the connected slots.
        :param args: The positional arguments to pass along (can be anything!)
        :param kwargs: The keyword arguments to pass along. (can be anything!)
        :return:
        """

        # Quickly make some private references to the collections we need to process.
        # Although the these fields are always safe to use read and use with regards to threading,
        # we want to operate on a consistent snapshot of the whole set of fields.
        with self.__lock:
            functions = self.__functions
            methods = self.__methods
            signals = self.__signals

        # Call handler functions
        for func in functions:
            func(*args, **kwargs)

        # Call handler methods
        for dest, func in methods:
            func(dest, *args, **kwargs)

        # Emit connected signals
        for signal in signals:
            signal.emit(*args, **kwargs)

    def connect(self, connector: Union["Signal", Callable[[], None]]) -> None:
        '''
        Connect something (anything, including another Signal) to this signal
        :param connector: The other thing to connect to.
        :return:
        '''
        with self.__lock:
            if isinstance(connector, Signal):
                if connector == self:
                    return
                self.__signals = self.__signals.append(connector)
            elif inspect.ismethod(connector):
                self.__methods = self.__methods.append(cast(Any, connector).__self__, cast(Any, connector).__func__)
            else:
                # Once again, update the list of functions using a whole new list.
                self.__functions = self.__functions.append(connector)

    def disconnect(self, connector: Union["Signal", Callable[[], None]]) -> None:
        '''
        Disconnect something from this signal
        :param connector: The signal or slot (function) to disconnect.
        :return:
        '''
        with self.__lock:
            if isinstance(connector, Signal):
                self.__signals = self.__signals.remove(connector)
            elif inspect.ismethod(connector):
                self.__methods = self.__methods.remove(cast(Any, connector).__self__, cast(Any, connector).__func__)
            else:
                self.__functions = self.__functions.remove(connector)

    def disconnectAll(self) -> None:
        '''
        Disconnect all connected slots (aka; reset)
        :return:
        '''
        with self.__lock:
            self.__functions = WeakImmutableList()
            self.__methods = WeakImmutablePairList()
            self.__signals = WeakImmutableList()

    # This __str__() is useful for debugging.
    # def __str__(self):
    #     function_str = ", ".join([repr(f) for f in self.__functions])
    #     method_str = ", ".join([ "{dest: " + str(dest) + ", funcs: " + strMethodSet(funcs) + "}" for dest, funcs in self.__methods])
    #     signal_str = ", ".join([str(signal) for signal in self.__signals])
    #     return "Signal<{}> {{ __functions={{ {} }}, __methods={{ {} }}, __signals={{ {} }} }}".format(id(self), function_str, method_str, signal_str)


def strMethodSet(method_set):
    return "{" + ", ".join([str(m) for m in method_set]) + "}"


def signalemitter(cls):
    '''
    Class decorator that ensures a class has unique instances of signals.

    Since signals need to be instance variables, normally you would need to create all
    signals in the class" `__init__` method. However, this makes them rather awkward to
    document. This decorator instead makes it possible to declare them as class variables,
    which makes documenting them near the function they are used possible. This decorator
    adjusts the class' __new__ method to create new signal instances for all class signals.
    :param cls:
    :return:
    '''
    # First, check if the base class has any signals defined
    signals = inspect.getmembers(cls, lambda i: isinstance(i, Signal))
    if not signals:
        raise TypeError("Class {0} is marked as signal emitter but no signal were found".format(cls))

    # Then, replace the class' new method with one that modifies the created instance to have
    # unique signals.
    old_new = cls.__new__

    def new_new(subclass, *args, **kwargs):
        if old_new == object.__new__:
            sub = object.__new__(subclass)
        else:
            sub = old_new(subclass, *args, **kwargs)

        for key, value in inspect.getmembers(cls, lambda i: isinstance(i, Signal)):
            setattr(sub, key, Signal())

        return sub

    cls.__new__ = new_new
    return cls


T = TypeVar("T")


class WeakImmutableList(Generic[T], Iterable):
    def __init__(self) -> None:
        """
        Minimal implementation of a weak reference list with immutable tendencies.

        Strictly speaking this isn't immutable because the garbage collector can modify
        it, but no application code can. Also, this class doesn't implement the Python
        list API, only the handful of methods we actually need in the code above.
        """
        self.__list = []    # type: List[ReferenceType[Optional[T]]]

    def append(self, item: T) -> "WeakImmutableList[T]":
        '''
        Append an item and return a new list
        :param item:
        :return:
        '''
        new_instance = WeakImmutableList()  # type: WeakImmutableList[T]
        new_instance.__list = self.__cleanList()
        new_instance.__list.append(weakref.ref(item))
        return new_instance

    ## Remove an item and return a list
    #
    #  Note that unlike the normal Python list.remove() method, this ones
    #  doesn't throw a ValueError if the item isn't in the list.
    #  \param item item to remove
    #  \return a list which does not have the item.
    def remove(self, item: T) -> "WeakImmutableList[T]":
        for item_ref in self.__list:
            if item_ref() is item:
                new_instance = WeakImmutableList()  # type: WeakImmutableList[T]
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(item_ref)
                return new_instance
        else:
            return self  # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self) -> "List[ReferenceType[Optional[T]]]":
        return [item_ref for item_ref in self.__list if item_ref() is not None]

    def __iter__(self):
        return WeakImmutableListIterator(self.__list)


## Iterator wrapper which filters out missing values.
#
# It dereferences each weak reference object and filters out the objects
# which have already disappeared via GC.
class WeakImmutableListIterator(Generic[T], Iterable):
    def __init__(self, list_):
        self.__it = list_.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        next_item = self.__it.__next__()()
        while next_item is None:    # Skip missing values
            next_item = self.__it.__next__()()
        return next_item


U = TypeVar('U')


##  A variation of WeakImmutableList which holds a pair of values using weak refernces.
class WeakImmutablePairList(Generic[T, U], Iterable):
    def __init__(self) -> None:
        self.__list = []  # type: List[Tuple[ReferenceType[T],ReferenceType[U]]]

    ## Append an item and return a new list
    #
    #  \param item the item to append
    #  \return a new list
    def append(self, left_item: T, right_item: U) -> "WeakImmutablePairList[T, U]":
        new_instance = WeakImmutablePairList()  # type: WeakImmutablePairList[T, U]
        new_instance.__list = self.__cleanList()
        new_instance.__list.append((weakref.ref(left_item), weakref.ref(right_item)))
        return new_instance

    ## Remove an item and return a list
    #
    #  Note that unlike the normal Python list.remove() method, this ones
    #  doesn't throw a ValueError if the item isn't in the list.
    #  \param item item to remove
    #  \return a list which does not have the item.
    def remove(self, left_item: T, right_item: U) -> "WeakImmutablePairList[T, U]":
        for pair in self.__list:
            left = pair[0]()
            right = pair[1]()

            if left is left_item and right is right_item:
                new_instance = WeakImmutablePairList()  # type: WeakImmutablePairList[T, U]
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(pair)
                return new_instance
        else:
            return self  # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self) -> List[Tuple[ReferenceType, ReferenceType]]:
        return [pair for pair in self.__list if pair[0]() is not None and pair[1]() is not None]

    def __iter__(self):
        return WeakImmutablePairListIterator(self.__list)


# A small iterator wrapper which dereferences the weak ref objects and filters
# out the objects which have already disappeared via GC.
class WeakImmutablePairListIterator:
    def __init__(self, list_):
        self.__it = list_.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        pair = self.__it.__next__()
        left = pair[0]()
        right = pair[1]()
        while left is None or right is None:    # Skip missing values
            pair = self.__it.__next__()
            left = pair[0]()
            right = pair[1]()

        return (left, right)