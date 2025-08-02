import sys
import time
from kubernetes.client.rest import ApiException
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import batch_v1

logger = setup_logger(__name__)


def wait_for_job_creation(job_name, job_namespace, timeout=120, poll_interval=5):
    start_time = time.monotonic()
    while True:
        try:
            batch_v1.read_namespaced_job(name=job_name, namespace=job_namespace)
            return
        except ApiException as e:
            if e.status == 404:
                continue
            else:
                logger.error(f"Exception when calling read_namespaced_job: {e}\n")
                sys.exit(1)

        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Timeout waiting for job {job_name} to be created in namespace {job_namespace}."
            )
        time.sleep(poll_interval)


def wait_for_job_termination(job_name, job_namespace, timeout=120, poll_interval=5):
    start_time = time.monotonic()
    while True:
        try:
            batch_v1.read_namespaced_job(name=job_name, namespace=job_namespace)
        except ApiException as e:
            if e.status == 404:
                return
            else:
                logger.error(f"Exception when calling read_namespaced_job: {e}\n")
                sys.exit(1)

        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Timeout waiting for job {job_name} to be deleted in namespace {job_namespace}."
            )
        time.sleep(poll_interval)
