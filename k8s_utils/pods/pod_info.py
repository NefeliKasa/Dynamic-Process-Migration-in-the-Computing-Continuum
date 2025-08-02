from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_pod_data(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return (pod.metadata, pod.spec)


def get_pod_status(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return pod.status


def get_pod_uid(pod_name, pod_namespace):
    pod_metadata, _ = get_pod_data(pod_name, pod_namespace)

    return pod_metadata.uid


def get_container_in_pod(pod_spec, container_name):
    for i, container in enumerate(pod_spec.containers):
        if container.name != container_name:
            continue
        else:
            return container


def get_container_id(pod_name, pod_namespace, container_name):
    pod_status = get_pod_status(pod_name, pod_namespace)

    container_statuses = pod_status.container_statuses
    if not container_statuses:
        logger.warning(
            f"No container statuses found for pod {pod_name} in namespace {pod_namespace}."
        )
        return None

    for container_status in container_statuses:
        if container_status.name == container_name:
            container_id = container_status.container_id

            if not container_id:
                logger.warning(
                    f"Container ID not found for container '{container_name}' in pod '{pod_name}'."
                )
                return None

            return container_status.container_id

    logger.warning(f"Container '{container_name}' not found in pod '{pod_name}'.")
    return None


def get_node_name(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return pod.spec.node_name


def get_node_ip(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return pod.status.host_ip
