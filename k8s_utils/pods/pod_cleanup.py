import os
import sys
import time
from kubernetes.client.rest import ApiException
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1

logger = setup_logger(__name__)


def wait_for_pod_termination(pod_name, pod_namespace, timeout=120, poll_interval=5):
    start_time = time.monotonic()
    while True:
        try:
            v1.read_namespaced_pod(name=pod_name, namespace=pod_namespace)
        except ApiException as e:
            if e.status == 404:
                return
            else:
                logger.error(f"Exception when calling read_namespaced_pod: {e}\n")
                sys.exit(1)

        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Timeout waiting for pod {pod_name} to be deleted in namespace {pod_namespace}."
            )
        time.sleep(poll_interval)


def check_for_main_container_termination(pod_name, pod_namespace, container_name):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    for i, container in enumerate(pod.spec.containers):
        if container.name != container_name:
            continue

        if pod.status.container_statuses is None:
            logger.error(
                f"Container status for {container.name} not found in pod {pod_name}."
            )
            break

        status = pod.status.container_statuses[i]
        state = status.state
        if state is None:
            logger.error(
                f"State for container {container.name} in pod {pod_name} is None."
            )
            break

        if state.terminated is not None:
            if state.terminated:
                return True


def delete_pod_if_main_container_terminated(pod_name, pod_namespace, container_name):
    if check_for_main_container_termination(pod_name, pod_namespace, container_name):
        logger.info(
            f"The main container {container_name} in pod {pod_name} is terminated. Deleting pod and exiting sidecar controller."
        )
        safe_kube_call(v1.delete_namespaced_pod, name=pod_name, namespace=pod_namespace)
        os._exit(0)
