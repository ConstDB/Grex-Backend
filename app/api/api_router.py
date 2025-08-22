from fastapi import APIRouter
from ..messages.routes import router as messages_router
from ..notifications.routes import router as notification_router
from ..summaries.routes import router as summaries_router
from ..tasks.routes import router as tasks_router
from ..users.user_routes import router as users_router
from ..users.auth_routes import router as auth_router
from ..workspaces.routes import router as workspaces_router



router = APIRouter()


router.include_router(messages_router, tags=["Messages"])
router.include_router(notification_router, prefix="/notification", tags=["Notification"])
router.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
router.include_router(auth_router, tags=["Authentication"])
router.include_router(users_router, tags=["Users"])
router.include_router(workspaces_router, prefix="/workspaces", tags=["Workspaces"])
