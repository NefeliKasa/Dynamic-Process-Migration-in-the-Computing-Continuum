import requests
import urllib3
from utils.logging_config import setup_logger
from k8s_utils.pods.pod_info import get_node_ip

logger = setup_logger(__name__)


def checkpoint_container(pod_name, pod_namespace, container_name):
    with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
        token = f.read().strip()

    headers = {"Authorization": f"Bearer {token}"}

    NODE_IP = get_node_ip(pod_name, pod_namespace)

    # Send a checkpoint request to the kubelet checkpoint API
    CHECKPOINT_URL = f"https://{NODE_IP}:10250/checkpoint/{pod_namespace}/{pod_name}/{container_name}"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.post(CHECKPOINT_URL, verify=False, headers=headers)

    if response.status_code == 200:
        logger.info("Checkpoint request was successful:", response.text)
    else:
        logger.error(
            f"Checkpoint request failed with status code {response.status_code}: {response.text}"
        )
        raise RuntimeError
