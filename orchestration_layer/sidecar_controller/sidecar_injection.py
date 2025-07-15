import os
from kubernetes import client
from utils.logging_config import setup_logger
from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from k8s_utils.pod_recreation import recreate_pod
from config import (
    MONITORING_INTERVAL,
    CPU_OBSERVATION_INTERVAL,
    MONITORING_TOPIC,
)
from constants import MONITOR_IMAGE, SERVICE_ACCOUNT_NAME

logger = setup_logger(__name__)


def build_env_vars():
    return [
        client.V1EnvVar(name="MONITORING_INTERVAL", value=MONITORING_INTERVAL),
        client.V1EnvVar(
            name="CPU_OBSERVATION_INTERVAL", value=CPU_OBSERVATION_INTERVAL
        ),
        client.V1EnvVar(name="MONITORING_TOPIC", value=MONITORING_TOPIC),
    ]


def build_container(env_vars):
    return client.V1Container(
        name="sidecar-container",
        image=MONITOR_IMAGE,
        env=env_vars,
        image_pull_policy="Always",
    )


def inject_sidecar_to_pod(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    pod.spec.service_account_name = SERVICE_ACCOUNT_NAME

    env_vars = build_env_vars()

    sidecar_container = build_container(env_vars)

    pod.spec.containers.append(sidecar_container)
    pod.spec.share_process_namespace = True  # In order to share the PID namespace of the main container with the sidecar container.

    recreate_pod(pod_name, pod_namespace, pod.metadata, pod.spec)
