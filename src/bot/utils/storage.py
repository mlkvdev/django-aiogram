import json
from typing import Dict, Any, Optional, cast

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from aiogram.fsm.storage.redis import KeyBuilder, DefaultKeyBuilder, _JsonLoads, _JsonDumps
from django.core.cache import cache
from redis.typing import ExpiryT


class DjangoRedisStorage(BaseStorage):
    def __init__(
            self,
            key_builder: Optional[KeyBuilder] = None,
            state_ttl: Optional[ExpiryT] = None,
            data_ttl: Optional[ExpiryT] = None,
            json_loads: _JsonLoads = json.loads,
            json_dumps: _JsonDumps = json.dumps,
    ):
        if key_builder is None:
            key_builder = DefaultKeyBuilder(with_destiny=True)
        self.key_builder = key_builder
        self.state_ttl = state_ttl
        self.data_ttl = data_ttl
        self.json_loads = json_loads
        self.json_dumps = json_dumps

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        redis_key = self.key_builder.build(key, "state")
        if state is None:
            await cache.adelete(redis_key)
        else:
            await cache.aset(
                redis_key,
                cast(str, state.state if isinstance(state, State) else state),
                self.state_ttl,
            )

    async def get_state(self, key: StorageKey) -> Optional[str]:
        redis_key = self.key_builder.build(key, "state")
        value = await cache.aget(redis_key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return cast(Optional[str], value)

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        redis_key = self.key_builder.build(key, "data")
        if not data:
            await cache.adelete(redis_key)
            return
        await cache.aset(
            redis_key,
            self.json_dumps(data),
            self.data_ttl,
        )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        redis_key = self.key_builder.build(key, "data")
        value = await cache.aget(redis_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return cast(Dict[str, Any], self.json_loads(value))

    async def close(self) -> None:
        await cache.aclose()