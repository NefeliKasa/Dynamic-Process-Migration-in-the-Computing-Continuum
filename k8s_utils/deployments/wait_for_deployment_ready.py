import sys
import time
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import app_v1

logger = setup_logger(__name__)


def wait_for_deployment_ready(
    deployment_name, deployment_namespace, timeout=120, poll_interval=5
):
    start_time = time.monotonic()
    while True:
        deployment = safe_kube_call(
            app_v1.read_namespaced_deployment,
            name=deployment_name,
            namespace=deployment_namespace,
            ignore_not_found=True,
        )

        if deployment is not None:
            desired_replicas = (
                deployment.spec.replicas if deployment.spec.replicas is not None else 1
            )
            available_replicas = deployment.status.available_replicas or 0
            ready_replicas = deployment.status.ready_replicas or 0

            if (
                ready_replicas == desired_replicas
                and available_replicas == desired_replicas
            ):
                logger.info(f"Deployment '{deployment_name}' is ready.")
                return

        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Timeout waiting for deployment {deployment_name} to become ready in namespace {deployment_namespace}."
            )
            sys.exit(1)
        time.sleep(poll_interval)
