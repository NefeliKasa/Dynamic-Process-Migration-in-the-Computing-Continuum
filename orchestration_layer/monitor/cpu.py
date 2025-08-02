import psutil
import time
import sys
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_cpu_core_quota(metrics_path="/sys/fs/cgroup"):
    cpu_max_path = f"{metrics_path}/cpu.max"
    try:
        with open(cpu_max_path, "r") as f:
            quota_str, period_str = f.read().strip().split()

            if quota_str == "max":
                return psutil.cpu_count(logical=True)
            else:
                quota = int(quota_str)
                period = int(period_str)
                return quota / period
    except FileNotFoundError:
        logger.error(f"CPU limit file not found at {cpu_max_path}.")
        sys.exit(1)


def get_container_cpu_utilization(interval=1):
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(interval)

    total_cpu_utilization_percent = 0.0
    for (
        proc
    ) in psutil.process_iter():  # Initialization of CPU percentage for all processes
        try:
            total_cpu_utilization_percent += proc.cpu_percent(None)
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            logger.warning(
                f"Access denied to process {proc.pid} ({proc.name()}). Skipping."
            )
            continue
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return total_cpu_utilization_percent


def get_adjusted_container_cpu_utilization(metrics_path="/sys/fs/cgroup", interval=1):
    quota_cores = get_cpu_core_quota(metrics_path)

    total_cpu_utilization_percent = get_container_cpu_utilization(interval)

    if quota_cores == 0:
        logger.error("CPU quota is set to 0, cannot calculate adjusted CPU utilization.")
        sys.exit(1)

    return total_cpu_utilization_percent / quota_cores


def get_node_cpu_utilization(interval=1):
    return psutil.cpu_percent(interval)
