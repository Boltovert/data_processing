from typing import AsyncIterator, Self, Callable, Any


class AppResource:
    async def connect(self):
        pass

    async def disconnect(self):
        pass

    @classmethod
    def resource(cls) -> Callable[[Any], AsyncIterator[Self]]:
        async def initializer(*args, **kwargs):
            resource = cls(*args, **kwargs)
            print(f"Connecting {cls.__name__}")
            try:
                await resource.connect()
            except Exception as e:
                print(f"failed to connect to {cls.__name__}: {e}")
            print(f"Connecting {cls.__name__} done")
            yield resource
            print(f"Disconnecting {cls.__name__}")
            await resource.disconnect()
            print(f"Disconnecting {cls.__name__} done")

        return initializer
