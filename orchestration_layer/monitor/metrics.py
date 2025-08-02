import os
import sys
from datetime import datetime
from k8s_utils.pods.pod_info import get_pod_uid, get_container_id
from utils.logging_config import setup_logger
from config import POD_NAME, POD_NAMESPACE, CONTAINER_NAME, HOST_POD_METRICS_MOUNT_PATH
from cpu import get_adjusted_container_cpu_utilization, get_node_cpu_utilization
from ram import get_adjusted_container_ram_utilization, get_node_ram_utilization

logger = setup_logger(__name__)


def get_metrics_path():
    pod_id = get_pod_uid(POD_NAME, POD_NAMESPACE)
    pod_id_systemd = pod_id.replace("-", "_")

    container_id = get_container_id(POD_NAME, POD_NAMESPACE, CONTAINER_NAME)

    if not pod_id or not container_id:
        logger.error("Failed to retrieve pod or container ID.")
        sys.exit(1)

    stripped_container_id = container_id.removeprefix("containerd://")
    container_search_path = f"cri-containerd-{stripped_container_id}.scope"

    pod_search_path = f"kubepods-besteffort-pod{pod_id_systemd}.slice"
    best_effort_metrics_path = f"{HOST_POD_METRICS_MOUNT_PATH}/kubepods-besteffort.slice/{pod_search_path}/{container_search_path}"

    if not os.path.exists(best_effort_metrics_path):
        pod_search_path = f"kubepods-burstable-pod{pod_id_systemd}.slice"
        burstable_metrics_path = f"{HOST_POD_METRICS_MOUNT_PATH}/kubepods-burstable.slice/{pod_search_path}/{container_search_path}"

        return burstable_metrics_path
    else:
        return best_effort_metrics_path


def build_metrics_message(cpu_observation_interval):
    metrics_path = get_metrics_path()

    return {
        "timestamp": datetime.now().isoformat(),
        "container_cpu_utilization": get_adjusted_container_cpu_utilization(
            metrics_path, cpu_observation_interval
        ),
        "container_ram_utilization": get_adjusted_container_ram_utilization(
            metrics_path
        ),
        "node_cpu_utilization": get_node_cpu_utilization(cpu_observation_interval),
        "node_ram_utilization": get_node_ram_utilization(),
    }
