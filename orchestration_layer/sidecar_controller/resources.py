import sys
from utils.logging_config import setup_logger
from container_migration.migrate_running_container import migrate_running_container
import shared
from config import (
    CPU_USAGE_THRESHOLD,
    RAM_USAGE_THRESHOLD,
    RESTORE_POLICY,
    POD_NAME,
    POD_NAMESPACE,
    CONTAINER_NAME,
    CHECKPOINTS_DIR_PATH,
)

logger = setup_logger(__name__)


def check_for_resources(monitor_data, consumer):
    # Check if the resource usage exceeds the defined thresholds.
    cpu_usage = monitor_data["cpu_usage"]
    ram_usage = monitor_data["ram_usage"]

    if ram_usage > RAM_USAGE_THRESHOLD or cpu_usage > CPU_USAGE_THRESHOLD:
        logger.info(
            f"Resource usage exceeded: CPU={cpu_usage}, RAM={ram_usage}. Initiating migration."
        )

        shared.migration_initiated = True

        try:
            migrate_running_container(
                POD_NAME,
                POD_NAMESPACE,
                CONTAINER_NAME,
                RESTORE_POLICY,
                CHECKPOINTS_DIR_PATH,
            )

            shared.exit_code = 0
        except Exception as e:
            shared.exit_code = 1

        consumer.stop_event = True
