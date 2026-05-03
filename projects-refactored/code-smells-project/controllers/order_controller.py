import logging
from middlewares.error_handler import ValidationError
from models import order_model
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)
_notifications = NotificationService()

VALID_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def list_all():
    return order_model.get_all()


def list_by_user(usuario_id):
    return order_model.get_by_user(usuario_id)


def create(usuario_id, itens):
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    result, error = order_model.create(usuario_id, itens)
    if error:
        raise ValidationError(error)
    _notifications.notify_new_order(usuario_id, result["pedido_id"])
    logger.info("Pedido criado: pedido_id=%s usuario_id=%s", result["pedido_id"], usuario_id)
    return result


def update_status(pedido_id, novo_status):
    if novo_status not in VALID_STATUSES:
        raise ValidationError(f"Status inválido. Válidos: {VALID_STATUSES}")
    order_model.update_status(pedido_id, novo_status)
    _notifications.notify_status_change(pedido_id, novo_status)
    logger.info("Pedido %s: status -> %s", pedido_id, novo_status)
