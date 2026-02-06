"""Notification reminder models"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class NotificationType(Base):
    """通知类型定义"""
    __tablename__ = "notification_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # medication, measurement, goal, tracking
    icon = Column(String(100))  # Emoji icon
    default_template = Column(Text)  # Default message template
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    """通知记录"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("notification_types.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    status = Column(String(20), default="pending")  # pending, sent, delivered, read, dismissed
    scheduled_for = Column(DateTime, nullable=False)  # When to send notification
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    type = relationship("NotificationType", backref="notifications")
    actions = relationship("NotificationAction", backref="notification", cascade="all, delete-orphan")


class NotificationAction(Base):
    """通知操作（按钮等）"""
    __tablename__ = "notification_actions"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    label = Column(String(100), nullable=False)
    action_type = Column(String(50))  # url, dismiss, mark_done, log_measurement, etc.
    action_data = Column(JSON)  # Additional data for the action
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notification = relationship("Notification", backref="actions")


class NotificationPreference(Base):
    """用户通知偏好设置"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    reminder_frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    reminder_time = Column(String(5))  # HH:MM format
    reminder_days = Column(JSON)  # Array of day numbers (for weekly)
    quiet_hours = Column(JSON)  # Array of hour ranges when not to notify
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(Base):
    """通知发送日志"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    channel = Column(String(50))  # email, push, sms, in_app
    status = Column(String(50))  # success, failed, skipped
    error_message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    response_data = Column(JSON)  # Response from notification service
    created_at = Column(DateTime, default=datetime.utcnow)
