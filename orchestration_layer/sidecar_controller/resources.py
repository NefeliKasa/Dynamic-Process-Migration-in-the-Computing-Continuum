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


def print_migration_messages(
    container_cpu_utilization,
    container_ram_utilization,
    node_cpu_utilization,
    node_ram_utilization,
    container_resources_exceeded,
    node_resources_exceeded,
):
    if container_resources_exceeded and node_resources_exceeded:
        logger.info(
            f"Both container and node resource usage exceeded: CONTAINER_CPU={container_cpu_utilization}, CONTAINER_RAM={container_ram_utilization}, NODE_CPU={node_cpu_utilization}, NODE_RAM={node_ram_utilization}. Initiating migration."
        )
    elif container_resources_exceeded:
        logger.info(
            f"Container resource usage exceeded: CONTAINER_CPU={container_cpu_utilization}, CONTAINER_RAM={container_ram_utilization}. Initiating migration."
        )
    elif node_resources_exceeded:
        logger.info(
            f"Node resource usage exceeded: NODE_CPU={node_cpu_utilization}, NODE_RAM={node_ram_utilization}. Initiating migration."
        )


def initiate_migration(
    consumer,
    container_cpu_utilization,
    container_ram_utilization,
    node_cpu_utilization,
    node_ram_utilization,
    container_resources_exceeded,
    node_resources_exceeded,
):
    print_migration_messages(
        container_cpu_utilization,
        container_ram_utilization,
        node_cpu_utilization,
        node_ram_utilization,
        container_resources_exceeded,
        node_resources_exceeded,
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


def check_for_resources(monitor_data, consumer):
    # Check if the either node or container resource usage exceeds the defined thresholds.
    container_cpu_utilization = monitor_data["container_cpu_utilization"]
    container_ram_utilization = monitor_data["container_ram_utilization"]

    container_resources_exceeded = False
    if (
        container_cpu_utilization > CPU_USAGE_THRESHOLD
        or container_ram_utilization > RAM_USAGE_THRESHOLD
    ):
        container_resources_exceeded = True

    node_cpu_utilization = monitor_data["node_cpu_utilization"]
    node_ram_utilization = monitor_data["node_ram_utilization"]

    node_resources_exceeded = False
    if (
        node_cpu_utilization > CPU_USAGE_THRESHOLD
        or node_ram_utilization > RAM_USAGE_THRESHOLD
    ):
        node_resources_exceeded = True

    if container_resources_exceeded or node_resources_exceeded:
        initiate_migration(
            consumer,
            container_cpu_utilization,
            container_ram_utilization,
            node_cpu_utilization,
            node_ram_utilization,
            container_resources_exceeded,
            node_resources_exceeded,
        )
