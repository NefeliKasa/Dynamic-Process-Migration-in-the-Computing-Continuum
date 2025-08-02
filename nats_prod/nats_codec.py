import sys
import json
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class NatsCodec:
    @staticmethod
    def encode(data):
        try:
            return json.dumps(data).encode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode data: {e}")
            sys.exit(1)

    @staticmethod
    def decode(data):
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to decode data: {e}")
            sys.exit(1)
