"""Notification and reminder API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Notification, NotificationAction, NotificationPreference
from app.services.notifications import (
    NotificationService, ReminderService,
    init_default_notification_types
)


router = APIRouter()


# ==================== Notification Preferences ====================

@router.get("/preferences/{user_id}")
async def get_notification_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户通知偏好设置"""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


@router.put("/preferences/{user_id}")
async def update_notification_preferences(
    user_id: int,
    preferences: dict,
    db: Session = Depends(get_db)
):
    """更新用户通知偏好"""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
    
    # Update allowed fields
    allowed_fields = [
        'email_enabled', 'push_enabled', 'sms_enabled',
        'reminder_frequency', 'reminder_time', 'reminder_days', 'quiet_hours'
    ]
    
    for field in allowed_fields:
        if field in preferences:
            setattr(prefs, field, preferences[field])
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prefs)
    
    return prefs


# ==================== Notifications ====================

@router.get("/pending/{user_id}")
async def get_pending_notifications(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取待发送通知（按发送时间排序）
    
    Args:
        user_id: 用户 ID
        limit: 返回数量限制
    """
    reminder_service = ReminderService(db)
    notifications = reminder_service.get_pending_notifications(user_id, limit)
    
    return {
        "user_id": user_id,
        "notifications": notifications,
        "total": len(notifications)
    }


@router.post("/create")
async def create_notification(
    user_id: int,
    type_name: str,
    title: str,
    message: str,
    scheduled_for: Optional[str] = None,
    priority: str = "normal",
    db: Session = Depends(get_db)
):
    """
    手动创建通知
    
    Args:
        user_id: 用户 ID
        type_name: 通知类型名称
        title: 标题
        message: 消息内容
        scheduled_for: 计划发送时间（ISO format，None 为立即发送）
        priority: 优先级（low, normal, high, urgent）
    """
    notification_service = NotificationService(db)
    
    try:
        notification = notification_service.create_notification(
            user_id=user_id,
            type_name=type_name,
            title=title,
            message=message,
            scheduled_for=datetime.fromisoformat(scheduled_for) if scheduled_for else None,
            priority=priority
        )
        
        return {
            "success": True,
            "notification_id": notification.id,
            "message": "Notification created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{notification_id}/send")
async def send_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    发送通知
    
    Args:
        notification_id: 通知 ID
    """
    notification_service = NotificationService(db)
    
    success = notification_service.send_notification(notification_id)
    
    return {
        "success": success,
        "message": "Notification sent successfully" if success else "Notification send failed"
    }


@router.post("/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    拒记通知为已读
    
    Args:
        notification_id: 通知 ID
    """
    notification_service = NotificationService(db)
    
    success = notification_service.dismiss_notification(notification_id, notification_id)
    
    if success:
        return {
            "success": True,
            "message": "Notification dismissed"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )


@router.get("/history/{user_id}")
async def get_notification_history(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取用户通知历史
    
    Args:
        user_id: 用户 ID
        limit: 返回数量限制
    """
    reminder_service = ReminderService(db)
    notifications = reminder_service.get_user_notification_history(user_id, limit)
    
    return {
        "user_id": user_id,
        "notifications": notifications,
        "total": len(notifications)
    }


# ==================== Reminders ====================

@router.post("/reminders/medication")
async def create_medication_reminder(
    user_id: int,
    medication_name: str,
    reminder_times: List[str],
    note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    创建用药提醒
    
    Args:
        user_id: 用户 ID
        medication_name: 药物名称
        reminder_times: 提醒时间列表（HH:MM 格式，如 ["08:00", "20:00"]）
        note: 备注
    """
    reminder_service = ReminderService(db)
    
    notifications = reminder_service.create_medication_reminder(
        user_id=user_id,
        medication_name=medication_name,
        reminder_times=reminder_times,
        note=note
    )
    
    return {
        "success": True,
        "notifications_created": len(notifications),
        "message": f"Created {len(notifications)} medication reminders"
    }


@router.post("/reminders/measurement")
async def create_measurement_reminder(
    user_id: int,
    metric_name: str,
    frequency: str = "daily",
    target_time: Optional[str] = None,
    metric_target_value: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    创建测量提醒
    
    Args:
        user_id: 用户 ID
        metric_name: 测量指标名称（如 "血压"、"体重"）
        frequency: 频率（daily, weekly, monthly）
        target_time: 目标时间（HH:MM 格式，如 "08:00"）
        metric_target_value: 目标值（用于提醒用户）
    """
    reminder_service = ReminderService(db)
    
    notification = reminder_service.create_measurement_reminder(
        user_id=user_id,
        metric_name=metric_name,
        frequency=frequency,
        target_time=target_time,
        metric_target_value=metric_target_value
    )
    
    return {
        "success": True,
        "notification_id": notification.id,
        "message": f"Created measurement reminder for {metric_name}"
    }


@router.post("/reminders/goal")
async def create_goal_reminder(
    user_id: int,
    goal_type: str,
    goal_target: str,
    target_date: str,
    days_before: int = 3,
    db: Session = Depends(get_db)
):
    """
    创建目标截止提醒
    
    Args:
        user_id: 用户 ID
        goal_type: 目标类型
        goal_target: 目标描述
        target_date: 目标日期（ISO format）
        days_before: 提前几天提醒
    """
    reminder_service = ReminderService(db)
    
    # Parse target date
    try:
        target_dt = datetime.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid target_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    notification = reminder_service.create_goal_reminder(
        user_id=user_id,
        goal_type=goal_type,
        goal_target=goal_target,
        target_date=target_dt,
        days_before=days_before
    )
    
    return {
        "success": True,
        "notification_id": notification.id,
        "message": f"Created goal reminder for {goal_type}"
    }


# ==================== Notification Types ====================

@router.get("/types")
async def get_notification_types(db: Session = Depends(get_db)):
    """获取所有通知类型"""
    from app.models.notifications import NotificationType
    
    types = db.query(NotificationType).order_by(NotificationType.name).all()
    
    return {
        "types": [{
            "id": t.id,
            "name": t.name,
            "icon": t.icon,
            "default_template": t.default_template
        } for t in types]
    }


@router.post("/types")
async def create_notification_type(
    name: str,
    icon: Optional[str] = None,
    default_template: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    创建新的通知类型
    
    Args:
        name: 类型名称
        icon: Emoji 图标（可选）
        default_template: 默认消息模板（可选）
    """
    from app.models.notifications import NotificationType
    
    # Check if type already exists
    existing = db.query(NotificationType).filter(NotificationType.name == name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Notification type '{name}' already exists"
        )
    
    notification_type = NotificationType(
        name=name,
        icon=icon or "📌",
        default_template=default_template or ""
    )
    
    db.add(notification_type)
    db.commit()
    db.refresh(notification_type)
    
    return notification_type


# ==================== System ====================

@router.post("/init-default-types")
async def initialize_default_types(db: Session = Depends(get_db)):
    """
    初始化默认通知类型
    """
    init_default_notification_types(db)
    
    return {
        "success": True,
        "message": "Default notification types initialized"
    }
