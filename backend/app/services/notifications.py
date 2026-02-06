"""Notification reminder service"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database import get_db
from app.models.notifications import (
    Notification, NotificationAction, NotificationPreference,
    NotificationLog, NotificationType
)


class NotificationService:
    """通知服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        type_name: str,
        title: str,
        message: str,
        scheduled_for: Optional[datetime] = None,
        priority: str = "normal"
    ) -> Notification:
        """
        创建通知
        
        Args:
            user_id: 用户 ID
            type_name: 通知类型名称
            title: 标题
            message: 消息内容
            scheduled_for: 计划发送时间（None 为立即发送）
            priority: 优先级（low, normal, high, urgent）
        """
        # Get notification type
        notif_type = self.db.query(NotificationType).filter(
            NotificationType.name == type_name
        ).first()
        
        if not notif_type:
            raise Exception(f"Notification type '{type_name}' not found")
        
        notification = Notification(
            user_id=user_id,
            type_id=notif_type.id,
            title=title,
            message=message,
            priority=priority,
            status="pending",
            scheduled_for=scheduled_for
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def send_notification(self, notification_id: int) -> bool:
        """
        发送通知（根据用户偏好）
        
        Args:
            notification_id: 通知 ID
        
        Returns:
            是否发送成功
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            return False
        
        # Get user notification preferences
        prefs = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == notification.user_id
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = NotificationPreference(user_id=notification.user_id)
            self.db.add(prefs)
            self.db.commit()
        
        channels_used = []
        
        # Try email
        if prefs.email_enabled:
            try:
                success = self._send_email(notification, notification.user_id)
                if success:
                    channels_used.append("email")
                    self._log_notification_action(
                        notification_id, "email", "success", None
                    )
            except Exception as e:
                self._log_notification_action(
                    notification_id, "email", "failed", str(e)
                )
        
        # Try push notification
        if prefs.push_enabled:
            success = self._send_push_notification(notification)
            if success:
                channels_used.append("push")
                self._log_notification_action(
                    notification_id, "push", "success", None
                )
            else:
                self._log_notification_action(
                    notification_id, "push", "failed", "Push not configured"
                )
        
        # Try SMS
        if prefs.sms_enabled:
            success = self._send_sms_notification(notification, notification.user_id)
            if success:
                channels_used.append("sms")
                self._log_notification_action(
                    notification_id, "sms", "success", None
                )
        
        # Update notification status
        if channels_used:
            notification now = datetime.utcnow()
            notification.status = "delivered"
            notification.sent_at = now
            notification.delivered_at = now
            
            # Send in-app notification if applicable
            self._send_in_app_notification(notification)
            
        else:
            notification.status = "failed"
        
        self.db.commit()
        
        return len(channels_used) > 0
    
    def _send_email(
        self,
        notification: Notification,
        user_id: int
    ) -> bool:
        """
        发送邮件通知（需要配置 SMTP）
        
        Args:
            notification: 通知对象
            user_id: 用户 ID
        
        Returns:
            是否发送成功
        """
        # TODO: Configure SMTP settings
        # For demo, just log
        print(f"[Email] To user {user_id}: {notification.title}")
        return True  # Demo: always return True
    
    def _send_push_notification(self, notification: Notification) -> bool:
        """
        发送推送通知（需要配置 Push 服务）
        
        Args:
            notification: 通知对象
        
        Returns:
            是否发送成功
        """
        # TODO: Configure FCM/APNS
        print(f"[Push] Notification: {notification.title}")
        return True  # Demo: always return True
    
    def _send_sms_notification(
        self,
        notification: Notification,
        user_id: int
    ) -> bool:
        """
        发送短信通知（需要配置 SMS 服务）
        
        Args:
            notification: 通知对象
            user_id: 用户 ID
        
        Returns:
            是否发送成功
        """
        # TODO: Configure SMS service
        print(f"[SMS] To user {user_id}: {notification.title}")
        return False  # Demo: SMS not configured
    
    def _send_in_app_notification(self, notification: Notification):
        """
        发送应用内通知（保存记录）
        
        Args:
            notification: 通知对象
        """
        # Create read action
        action = NotificationAction(
            notification_id=notification.id,
            label="标记为已读",
            action_type="mark_read"
        )
        self.db.add(action)
        self.db.commit()
    
    def _log_notification_action(
        self,
        notification_id: int,
        channel: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """
        记录通知发送日志
        
        Args:
            notification_id: 通知 ID
            channel: 发送渠道
            status: 状态（success, failed, skipped）
            error_message: 错误消息
        """
        log = NotificationLog(
            notification_id=notification_id,
            channel=channel,
            status=status,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()


class ReminderService:
    """提醒服务（用药、测量、目标等）"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_medication_reminder(
        self,
        user_id: int,
        medication_name: str,
        reminder_times: List[str],  # List of HH:MM format
        note: Optional[str] = None
    ) -> List[Notification]:
        """
        创建用药提醒
        
        Args:
            user_id: 用户 ID
            medication_name: 药物名称
            reminder_times: 提醒时间列表（HH:MM 格式）
            note: 备注
        
        Returns:
            创建的通知列表
        """
        notifications = []
        
        # Get or create medication reminder type
        notif_type = self.db.query(NotificationType).filter(
            NotificationType.name == "medication"
        ).first()
        
        if not notif_type:
            notif_type = NotificationType(
                name="medication",
                icon="💊",
                default_template="是时候服用 {medication_name}了"
            )
            self.db.add(notif_type)
            self.db.commit()
            self.db.refresh(notif_type)
        
        for time_str in reminder_times:
            # Parse time
            try:
                hour, minute = map(int, time_str.split(":"))
            except ValueError:
                continue
            
            # Schedule for today
            now = datetime.utcnow()
            scheduled_for = datetime(
                now.year, now.month, now.day, hour, minute,
                tzinfo=now.tzinfo
            )
            
            # If scheduled for today has passed, schedule for tomorrow
            if scheduled_for < now:
                scheduled_for += timedelta(days=1)
            
            message = {
                "medication": medication_name,
                "time": time_str,
                "note": note
            }
            
            notification = Notification(
                user_id=user_id,
                type_id=notif_type.id,
                title=f"用药提醒: {medication_name}",
                message=f"是时候服用 {medication_name} 了（{time_str}）",
                priority="high",
                status="pending",
                scheduled_for=scheduled_for
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            notifications.append(notification)
        
        return notifications
    
    def create_measurement_reminder(
        self,
        user_id: int,
        metric_name: str,
        frequency: str = "daily",  # daily, weekly, monthly
        target_time: Optional[str] = None,  # HH:MM
        metric_target_value: Optional[float] = None
    ) -> Notification:
        """
        创建测量提醒
        
        Args:
            user_id: 用户 ID
            metric_name: 测量指标名称
            frequency: 频率（daily, weekly, monthly）
            target_time: 目标时间
            metric_target_value: 目标值
        
        Returns:
            创建的通知
        """
        # Get or create measurement reminder type
        notif_type = self.db.query(NotificationType).filter(
            NotificationType.name == "measurement"
        ).first()
        
        if not notif_type:
            notif_type = NotificationType(
                name="measurement",
                icon="📊",
                default_template="请记录您的 {metric_name}"
            )
            self.db.add(notif_type)
            self.db.commit()
            self.db.refresh(notif_type)
        
        message = f"请记录您的 {metric_name} 测量"
        if metric_target_value:
            message += f"（目标值：{metric_target_value}）"
        
        frequency_map = {
            "daily": "每天",
            "weekly": "每周",
            "monthly": "每月"
        }
        
        title = {
            "daily": "每日测量提醒",
            "weekly": "每周测量提醒",
            "monthly": "每月测量提醒"
        }[frequency]
        
        notification = Notification(
            user_id=user_id,
            type_id=notif_type.id,
            title=title.get(frequency, "测量提醒"),
            message=message,
            priority="normal",
            status="pending"
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def create_goal_reminder(
        self,
        user_id: int,
        goal_type: str,
        goal_target: str,
        target_date: datetime,
        days_before: int = 3
    ) -> Notification:
        """
        创建目标截止提醒
        
        Args:
            user_id: 用户 ID
            goal_type: 目标类型
            goal_target: 目标描述
            target_date: 目标日期
            days_before: 提前几天提醒
        
        Returns:
            创建的通知
        """
        # Get reminder date
        reminder_date = target_date - timedelta(days=days_before)
        
        # Get or create goal reminder type
        notif_type = self.db.query(NotificationType).filter(
            NotificationType.name == "goal"
        ).first()
        
        if not notif_type:
            notif_type = NotificationType(
                name="goal",
                icon="🎯",
                default_template="距离目标还有 {days_before} 天"
            )
            self.db.add(notif_type)
            self.db.commit()
            self.db.refresh(notif_type)
        
        notification = Notification(
            user_id=user_id,
            type_id=notif_type.id,
            title=f"目标提醒: {goal_type}",
            message=f"距离目标 '{goal_target}' 还有 {days_before} 天",
            priority="high",
            status="pending",
            scheduled_for=reminder_date
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_pending_notifications(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Notification]:
        """
        获取待发送通知（按时间排序）
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
        
        Returns:
            待发送通知列表
        """
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.status == "pending",
            Notification.scheduled_for <= datetime.utcnow()
        ).order_by(
            Notification.scheduled_for.asc()
        ).limit(limit).all()
        
        return notifications
    
    def dismiss_notification(self, notification_id: int, user_id: int) -> bool:
        """
        标记通知为已读
        
        Args:
            notification_id: 通知 ID
            user_id: 用户 ID
        
        Returns:
            是否成功
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.status = "dismissed"
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_user_notification_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Notification]:
        """
        获取用户通知历史
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
        
        Returns:
            通知历史列表
        """
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        return notifications


# Predefined notification types
DEFAULT_NOTIFICATION_TYPES = [
    {"name": "medication", "icon": "💊", "default_template": "是时候服用 {medication}了"},
    {"name": "measurement", "icon": "📊", "default_template": "请记录您的 {metric_name}"},
    {"name": "goal", "icon": "🎯", "default_template": "距离目标还有 {days} 天"},
    {"name": "tracking_start", "icon": "▶️", "default_template": "开始干预措施: {intervention}"},
    {"name": "tracking_end", "icon": "✅", "default_template": "干预措施完成: {intervention}"},
    {"name": "measurement_anomaly", "icon": "⚠️", "default_template": "测量值异常: {metric} = {value}"}
]


def init_default_notification_types(db: Session):
    """初始化默认通知类型"""
    for type_data in DEFAULT_NOTIFICATION_TYPES:
        existing = db.query(NotificationType).filter(
            NotificationType.name == type_data["name"]
        ).first()
        
        if not existing:
            notif_type = NotificationType(
                name=type_data["name"],
                icon=type_data["icon"],
                default_template=type_data["default_template"]
            )
            db.add(notif_type)
    
    db.commit()
