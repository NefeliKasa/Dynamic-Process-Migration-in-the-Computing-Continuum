import sys
import asyncio
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


async def safe_nats_call(func, *args, retries=3, delay=2, log_args=False, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            message = (
                f"Exception when calling {func.__name__} (attempt {attempt}/{retries})"
            )
            if log_args:
                message += f" with args={args} kwargs={kwargs}"
            logger.error(f"{message}: {e}")
            if attempt == retries:
                logger.error("Max retries reached. Exiting.")
                sys.exit(1)
            await asyncio.sleep(delay)
