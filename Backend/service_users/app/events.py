# Simple event publisher stub. Replace with real broker later.
import logging
logger = logging.getLogger("events")

def publish_user_created(user):
    logger.info("event.user.created", extra={"user_id": user.id, "email": user.email})
