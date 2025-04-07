import contextlib

from bot.misc import on_startup, on_shutdown


@contextlib.asynccontextmanager
async def lifespan_context():
    try:
        await on_startup()
        yield
    finally:
        await on_shutdown()
