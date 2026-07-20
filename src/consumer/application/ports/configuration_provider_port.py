from abc import ABC, abstractmethod

from consumer.domain.value_objects import SessionConfiguration


class ConfigurationProviderPort(ABC):
    @abstractmethod
    async def load(self) -> SessionConfiguration: ...

    @abstractmethod
    async def reload(self) -> SessionConfiguration: ...
