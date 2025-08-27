from fastapi import APIRouter
from ..messages.routes import router as messages_router
from ..notifications.routes import router as notification_router
from ..summaries.routes import router as summaries_router
from ..task.routes.task_router import router as task_router
from ..task.routes.task_attachment_router import router as task_attachment_router
from ..task.routes.task_comment_router import router as task_comment_router
from ..task.routes.sub_task_router import router as sub_task_router
from ..task.routes.task_assignment_router import router as task_assignment_router
from ..users.user_routes import router as users_router
from ..users.auth_routes import router as auth_router
from ..workspaces.routes import router as workspaces_router


router = APIRouter()


router.include_router(messages_router, prefix="/messages", tags=["Messages"])
router.include_router(notification_router, prefix="/notification", tags=["Notification"])
router.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])
router.include_router(task_router, prefix="/tasks", tags=["Task"])
router.include_router(task_attachment_router, tags=["Task Attachment"])
router.include_router(task_comment_router, tags=["TaskComment"])
router.include_router(sub_task_router, tags=["SubTask"])
router.include_router(task_assignment_router, tags=["TaskAssignment"])
router.include_router(auth_router, tags=["Authentication"])
router.include_router(users_router, tags=["Users"])
router.include_router(workspaces_router, prefix="/workspaces", tags=["Workspaces"])