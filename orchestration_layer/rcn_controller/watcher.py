import time
from kubernetes import watch
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import custom_obj_api
from controller import (
    create_pod_controller,
    patch_pod_controller,
    delete_pod_controller,
)
from constants import GROUP, VERSION, PLURAL

logger = setup_logger(__name__)


def watch_edge_nodes():
    w = watch.Watch()
    while True:
        try:
            stream = w.stream(
                custom_obj_api.list_cluster_custom_object,
                GROUP,
                VERSION,
                PLURAL,
                timeout_seconds=300,
            )

            for event in stream:
                rcn = event["object"]
                event_type = event["type"]

                if event_type == "ADDED":
                    logger.info(f"EdgeNode {rcn['metadata']['name']} added.")
                    create_pod_controller(rcn)
                elif event_type == "MODIFIED":
                    logger.info(f"EdgeNode {rcn['metadata']['name']} modified.")
                    patch_pod_controller(rcn)
                elif event_type == "DELETED":
                    logger.info(f"EdgeNode {rcn['metadata']['name']} deleted.")
                    delete_pod_controller(rcn)
        except Exception as e:
            logger.warning(f"Watcher error or timeout, reconnecting: {e}")
            time.sleep(2)
