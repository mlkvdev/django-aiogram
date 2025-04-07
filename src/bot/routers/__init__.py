from aiogram import Router

from .main import router as main_router

_routers = (
    main_router,
)
router = Router()
router.include_routers(*_routers)
