import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def notify_new_order(self, usuario_id: int, pedido_id: int) -> None:
        logger.info("Pedido criado: pedido_id=%s usuario_id=%s", pedido_id, usuario_id)

    def notify_status_change(self, pedido_id: int, novo_status: str) -> None:
        logger.info("Status atualizado: pedido_id=%s status=%s", pedido_id, novo_status)
