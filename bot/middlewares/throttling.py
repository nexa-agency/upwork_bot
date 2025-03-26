import asyncio
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5):
        self.limit = limit
        self.cache: Dict[str, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Если пользователь флудит, то не даем ему отправлять сообщения.
        """
        throttling_flag = get_flag(data, "throttling_key")
        if throttling_flag is None:
            throttling_key = f"{event.chat.id}:{event.from_user.id}"
        else:
            throttling_key = throttling_flag

        if throttling_key in self.cache and (asyncio.get_event_loop().time() - self.cache[throttling_key]) < self.limit:
            return
        
        self.cache[throttling_key] = asyncio.get_event_loop().time()
        return await handler(event, data)