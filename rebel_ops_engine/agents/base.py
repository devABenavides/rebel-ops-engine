from abc import ABC, abstractmethod

from models import Message


class Agent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def process(self, message: Message) -> Message:
        pass
