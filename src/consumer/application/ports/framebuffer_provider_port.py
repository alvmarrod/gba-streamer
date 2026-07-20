from abc import ABC, abstractmethod


class FramebufferProviderPort(ABC):
    @abstractmethod
    async def get_framebuffer(self) -> bytes: ...
