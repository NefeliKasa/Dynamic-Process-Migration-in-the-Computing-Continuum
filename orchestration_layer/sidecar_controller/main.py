import sys
import asyncio
import threading
from utils.logging_config import setup_logger
from sidecar_injection import inject_sidecar_to_pod
from cleanup import cleanup
from nats_prod.nats_consumer import NatsConsumer as Consumer
from resources import check_for_resources
import shared
from config import POD_NAME, POD_NAMESPACE, CONTAINER_NAME
from constants import MONITORING_TOPIC

logger = setup_logger(__name__)


async def main():
    # We inject a sidecar into the pod to monitor the resource usage of the main container.
    # The sidecar will send the monitoring data to the controller, which will make migration decisions based on the data.
    inject_sidecar_to_pod(POD_NAME, POD_NAMESPACE)

    threading.Thread(
        target=cleanup,
        args=(POD_NAME, POD_NAMESPACE, CONTAINER_NAME),
        daemon=True,
    ).start()

    consumer = Consumer([MONITORING_TOPIC], check_for_resources, json_decode=True)

    try:
        await consumer.consume()
    except Exception as e:
        consumer.close()
        sys.exit(1)

    sys.exit(shared.exit_code)


if __name__ == "__main__":
    asyncio.run(main())
