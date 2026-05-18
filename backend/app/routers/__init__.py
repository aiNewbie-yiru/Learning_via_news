from app.routers.articles import router as articles_router
from app.routers.comments import router as comments_router
from app.routers.chat import router as chat_router
from app.routers.favorites import router as favorites_router

__all__ = ["articles_router", "comments_router", "chat_router", "favorites_router"]
