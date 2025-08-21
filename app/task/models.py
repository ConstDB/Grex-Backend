# # app/models/task.py

# from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Float
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.db.base import Base


# class Task(Base):
#     __tablename__ = "tasks"

#     task_id = Column(Integer, primary_key=True, index=True)
#     workspace_id = Column(Integer, ForeignKey("workspaces.workspace_id"), nullable=False)
#     subject = Column(String(100), nullable=True)
#     title = Column(String(200), nullable=False)
#     description = Column(Text, nullable=True)
#     deadline = Column(DateTime, nullable=True)
#     status = Column(String(20), default="pending")  # pending/done/overdue
#     priority_level = Column(String(20), nullable=True)
#     created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     marked_done_at = Column(DateTime, nullable=True)

#     # Relationships
#     subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
#     assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
#     attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
#     comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
#     logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")


# class SubTask(Base):
#     __tablename__ = "subtasks"

#     subtask_id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
#     description = Column(Text, nullable=False)
#     is_done = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     task = relationship("Task", back_populates="subtasks")


# class TaskAssignment(Base):
#     __tablename__ = "task_assignments"

#     task_id = Column(Integer, ForeignKey("tasks.task_id"), primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

#     task = relationship("Task", back_populates="assignments")


# class TaskComment(Base):
#     __tablename__ = "task_comments"

#     comment_id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)  # missing in ERD!
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

#     task = relationship("Task", back_populates="comments")


# class TaskLog(Base):
#     __tablename__ = "task_logs"

#     task_log_id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)  # I added this for linking logs to tasks
#     workspace_id = Column(Integer, ForeignKey("workspaces.workspace_id"), nullable=False)
#     context = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     task = relationship("Task", back_populates="logs")


# class TaskAttachment(Base):
#     __tablename__ = "task_attachments"

#     attachment_id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
#     uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
#     file_url = Column(String(255), nullable=False)
#     file_type = Column(String(50), nullable=False)  # image/pdf/docs
#     file_size_mb = Column(Float, nullable=True)
#     uploaded_at = Column(DateTime, default=datetime.utcnow)

#     task = relationship("Task", back_populates="attachments")
