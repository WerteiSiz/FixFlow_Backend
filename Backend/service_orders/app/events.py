import logging
logger = logging.getLogger("events")

def publish_order_created(order):
    logger.info("event.order.created", extra={"order_id": order.id, "user_id": order.user_id})

def publish_order_status_changed(order):
    logger.info("event.order.status_changed", extra={"order_id": order.id, "status": order.status})
