import logging
import smtplib
from datetime import datetime

from config.settings import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not SMTP_USER or not SMTP_PASSWORD:
            logger.warning('SMTP credentials not configured; skipping email to %s', to)
            return False
        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            message = f'Subject: {subject}\n\n{body}'
            server.sendmail(SMTP_USER, to, message)
            server.quit()
            logger.info('Email sent to %s', to)
            return True
        except Exception as e:
            logger.exception('Failed to send email to %s', to)
            return False

    def notify_task_assigned(self, user, task) -> None:
        subject = f'Nova task atribuída: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}'
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.utcnow(),
        })

    def notify_task_overdue(self, user, task) -> None:
        subject = f'Task atrasada: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' está atrasada!\n\n"
            f'Data limite: {task.due_date}'
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id: int) -> list:
        return [n for n in self.notifications if n['user_id'] == user_id]
