import httpx


class HTTPXClientWrapper:
    async_client = None

    def start(self):
        self.async_client = httpx.AsyncClient()

    async def stop(self):
        await self.async_client.aclose()
        self.async_client = None

    def __call__(self):
        assert self.async_client is not None
        return self.async_client
