from __future__ import annotations

import weakref
from abc import ABC, abstractmethod


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class ConcreteSubject(Subject):
    def __init__(self):
        self._observers = weakref.WeakSet()

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.add(observer)

    def detach(self, observer: Observer) -> None:
        print("Subject: Detached an observer.")
        self._observers.discard(observer)

    def notify(self) -> None:
        for observer in list(self._observers):
            observer.update(self)


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass
