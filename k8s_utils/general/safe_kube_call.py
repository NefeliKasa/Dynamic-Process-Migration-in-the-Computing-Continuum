import sys
import time
from kubernetes.client.rest import ApiException
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def safe_kube_call(
    func,
    *args,
    retries=3,
    delay=2,
    ignore_conflict=False,
    ignore_not_found=False,
    **kwargs,
):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except ApiException as e:
            if ignore_conflict and e.status == 409:
                logger.info(
                    f"{func.__name__}: Resource already exists, skipping creation."
                )
                return
            if ignore_not_found and e.status == 404:
                logger.info(f"{func.__name__}: Resource not found, skipping deletion.")
                return

            logger.error(
                f"Exception when calling {func.__name__} (attempt {attempt}/{retries}): {e}"
            )
            if attempt == retries:
                logger.error("Max retries reached. Exiting.")
                sys.exit(1)
            time.sleep(delay)
