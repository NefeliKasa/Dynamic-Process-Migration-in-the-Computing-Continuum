from k8s_utils.pods.pod_cleanup import delete_pod_if_main_container_terminated
import shared
import time


def cleanup(POD_NAME, POD_NAMESPACE, CONTAINER_NAME):
    check_interval = 5

    while True:
        time.sleep(check_interval)

        if (
            not shared.migration_initiated
        ):  # We only perform cleanup if migration is not initiated. In case migration is initiated, the sidecar will handle the cleanup.
            delete_pod_if_main_container_terminated(
                POD_NAME, POD_NAMESPACE, CONTAINER_NAME
            )
        else:
            return
