import time
from kubernetes import watch
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1
from controller import create_sidecar_controller
from constants import EXCLUDED_APPS
from config import RCN_NAME, NAMESPACE
from signals import sigterm_received

logger = setup_logger(__name__)


def check_if_pod_is_valid_sidecar_target(pod):
    # The pods should run on edge layer nodes and belong to the rcn corresponding node group.
    # We ignore system related apps or recreated pods.
    if (
        pod.metadata.namespace == NAMESPACE
        and pod.spec.node_selector
        and pod.spec.node_selector.get("layer") == "edge"
        and pod.spec.node_selector.get("node-group") == RCN_NAME
        and (
            pod.metadata.labels == None
            or (
                (
                    pod.metadata.labels.get("recreated") == None
                    or pod.metadata.labels.get("recreated") != "yes"
                )
                and (
                    pod.metadata.labels.get("app") == None
                    or pod.metadata.labels.get("app") not in EXCLUDED_APPS
                )
            )
        )
    ):
        return True


def watch_pods():
    w = watch.Watch()
    while True:
        try:
            stream = w.stream(v1.list_namespaced_pod, namespace=NAMESPACE)

            for event in stream:
                if event["type"] == "ADDED":
                    pod = event["object"]

                    if check_if_pod_is_valid_sidecar_target(pod):
                        pod_name = pod.metadata.name
                        pod_namespace = pod.metadata.namespace
                        container_name = pod.spec.containers[0].name
                        create_sidecar_controller(
                            pod_name, pod_namespace, container_name
                        )

            if sigterm_received is True:
                exit(0)
        except Exception as e:
            logger.warning(f"Watcher error or timeout, reconnecting: {e}")
            time.sleep(2)
