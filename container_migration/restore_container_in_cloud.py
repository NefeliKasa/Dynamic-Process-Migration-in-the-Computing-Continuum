from k8s_utils.pods.pod_info import get_container_in_pod
from k8s_utils.pods.recreate_pod import recreate_pod


def restore_container_in_cloud(
    pod_metadata, pod_spec, container_name, image_name, is_deleted=False
):
    container = get_container_in_pod(pod_spec, container_name)

    container.image = image_name
    pod_spec.containers = [container]

    pod_spec.node_selector = {}
    pod_spec.node_selector["layer"] = "cloud"

    recreate_pod(
        pod_metadata.name,
        pod_metadata.namespace,
        pod_metadata,
        pod_spec,
        is_deleted,
    )
