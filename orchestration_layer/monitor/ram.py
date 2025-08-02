import psutil
import sys
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_ram_quota(metrics_path="/sys/fs/cgroup"):
    ram_max_path = f"{metrics_path}/memory.max"
    try:
        with open(ram_max_path, "r") as f:
            quota_str = f.read().strip()

            if quota_str == "max":
                return None
            else:
                return int(quota_str)
    except FileNotFoundError:
        logger.error(f"Memory limit file not found at {ram_max_path}.")
        sys.exit(1)


def get_current_ram_usage(metrics_path="/sys/fs/cgroup"):
    ram_current_path = f"{metrics_path}/memory.current"
    try:
        with open(ram_current_path, "r") as f:
            current_ram_utilization = int(f.read().strip())
            return current_ram_utilization

    except FileNotFoundError:
        logger.error(f"Current memory file not found at {ram_current_path}.")
        sys.exit(1)


def get_container_ram_utilization(metrics_path="/sys/fs/cgroup"):
    current_ram_usage = get_current_ram_usage(metrics_path)

    total_ram = psutil.virtual_memory().total

    if total_ram == 0:
        logger.error("Total RAM is 0, cannot calculate RAM utilization.")
        sys.exit(1)

    current_ram_utilization_percent = (current_ram_usage / total_ram) * 100
    return round(current_ram_utilization_percent, 1)


def get_adjusted_container_ram_utilization(metrics_path="/sys/fs/cgroup"):
    ram_quota = get_ram_quota(metrics_path)

    if ram_quota is None:
        return get_container_ram_utilization(metrics_path)

    current_ram_utilization = get_current_ram_usage(metrics_path)

    if ram_quota == 0:
        logger.error("RAM quota is set to 0, cannot calculate adjusted RAM utilization.")
        sys.exit(1)

    adjusted_ram_utilization_percent = (current_ram_utilization / ram_quota) * 100

    return round(adjusted_ram_utilization_percent, 1)


def get_node_ram_utilization():
    return psutil.virtual_memory().percent
