from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .ingredients import router as ingredients_router
from .tags import router as tags_router
from .recipes import router as recipes_router
from .favorites import router as favorites_router
from .followers import router as followers_router
from .shopping_list import router as shopping_list_router
from .subscriptions import router as subscriptions_router
from .files import router as files_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router, tags=["auth"])
router.include_router(users_router, tags=["users"])
router.include_router(ingredients_router, tags=["ingredients"])
router.include_router(recipes_router, tags=["recipes"])
router.include_router(favorites_router, tags=["favorites"])
router.include_router(followers_router, tags=["followers"])
router.include_router(shopping_list_router, tags=["shopping-list"])
router.include_router(subscriptions_router, tags=["subscriptions"])
router.include_router(files_router, tags=["files"])
router.include_router(tags_router, tags=["tags"])
