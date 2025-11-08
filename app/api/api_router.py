from fastapi import APIRouter
from ..messages.routes import router as messages_router
from ..notifications.routes.notif_router import router as notification_router
from ..notifications.routes.notif_recipient_router import router as notification_recipient_router
from ..categories.routes import router as category_router
from ..task.routes.task_router import router as task_router
from ..task.routes.task_comment_router import router as task_comment_router
from ..task.routes.sub_task_router import router as sub_task_router
from ..task.routes.task_assignment_router import router as task_assignment_router
from ..users.routes import router as users_router
from ..authentication.routes import router as auth_router
from ..workspaces.routes import router as workspaces_router
from ..messages.websocket import router as websocket_router
from ..pinned_messages.routes import router as pinned_router  
from ..quick_links.routes import router as link_router
from ..recent_activity.router import router as activity_router
from ..ai_assistant.routes import router as grex_router


router = APIRouter()

router.include_router(messages_router, tags=["Messages"])
router.include_router(notification_router, prefix="/notifications", tags=["Notification"])
router.include_router(notification_recipient_router, prefix="/notification-recipients", tags=["Notification Recipients"])
router.include_router(category_router, tags=["Category"])
router.include_router(task_router, prefix="/tasks", tags=["Task"])
router.include_router(task_comment_router, tags=["Task Comment"])
router.include_router(sub_task_router, tags=["SubTask"])
router.include_router(task_assignment_router, tags=["Task Assignment"])
router.include_router(auth_router, tags=["Authentication"])
router.include_router(users_router, tags=["Users"])
router.include_router(workspaces_router, tags=["Workspaces"])
router.include_router(websocket_router)
router.include_router(pinned_router, tags=["Pinned Messages"])
router.include_router(link_router, tags=["Quick Links"])
router.include_router(activity_router, tags=["Recent Activities"])
# router.include_router(grex_router, tags=["Grex AI"])

