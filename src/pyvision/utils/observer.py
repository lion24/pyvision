"""Defines the observer pattern classes for PyVision."""

from __future__ import annotations

import weakref
from abc import ABC, abstractmethod


class Subject(ABC):
    """Abstract base class for subjects that can be observed."""

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject.

        Args:
            observer (Observer): The observer to attach.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject.

        Args:
            observer (Observer): The observer to detach.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """Notify all attached observers."""
        pass


class ConcreteSubject(Subject):
    """Concrete implementation of a subject."""

    def __init__(self):
        """Initialize the ConcreteSubject object."""
        self._observers = weakref.WeakSet()

    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject.

        Args:
            observer (Observer): The observer to attach.
        """
        print("Subject: Attached an observer.")
        self._observers.add(observer)

    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject.

        Args:
            observer (Observer): The observer to detach.
        """
        print("Subject: Detached an observer.")
        self._observers.discard(observer)

    def notify(self) -> None:
        """Notify all attached observers."""
        for observer in list(self._observers):
            observer.update(self)


class Observer(ABC):
    """Abstract base class for observers."""

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """Update the observer with the latest state of the subject.

        Args:
            subject (Subject): The subject being observed.
        """
        pass
