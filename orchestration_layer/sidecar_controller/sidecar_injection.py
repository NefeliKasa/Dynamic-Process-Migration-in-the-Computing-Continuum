import os
from kubernetes import client
from utils.logging_config import setup_logger
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1
from k8s_utils.pods.recreate_pod import recreate_pod
from config import (
    POD_NAME,
    POD_NAMESPACE,
    CONTAINER_NAME,
    MONITORING_INTERVAL,
    CPU_OBSERVATION_INTERVAL,
)
from constants import (
    MONITOR_IMAGE,
    SERVICE_ACCOUNT_NAME,
    HOST_POD_METRICS_PATH,
    HOST_POD_METRICS_MOUNT_PATH,
    MONITORING_TOPIC,
)

logger = setup_logger(__name__)


def build_env_vars():
    return [
        client.V1EnvVar(name="POD_NAME", value=POD_NAME),
        client.V1EnvVar(name="POD_NAMESPACE", value=POD_NAMESPACE),
        client.V1EnvVar(name="CONTAINER_NAME", value=CONTAINER_NAME),
        client.V1EnvVar(
            name="HOST_POD_METRICS_MOUNT_PATH", value=HOST_POD_METRICS_MOUNT_PATH
        ),
        client.V1EnvVar(name="MONITORING_INTERVAL", value=MONITORING_INTERVAL),
        client.V1EnvVar(
            name="CPU_OBSERVATION_INTERVAL", value=CPU_OBSERVATION_INTERVAL
        ),
        client.V1EnvVar(name="MONITORING_TOPIC", value=MONITORING_TOPIC),
    ]


def build_volume_mount():
    return client.V1VolumeMount(
        name="host-pod-metrics", mount_path=HOST_POD_METRICS_MOUNT_PATH, read_only=True
    )


def build_container(env_vars, volume_mounts):
    return client.V1Container(
        name="sidecar-container",
        image=MONITOR_IMAGE,
        env=env_vars,
        image_pull_policy="Always",
        volume_mounts=volume_mounts,
    )


def build_hostpath_volume():
    return client.V1Volume(
        name="host-pod-metrics",
        host_path=client.V1HostPathVolumeSource(
            path=HOST_POD_METRICS_PATH, type="Directory"
        ),
    )


def inject_sidecar_to_pod(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    pod.spec.service_account_name = SERVICE_ACCOUNT_NAME

    env_vars = build_env_vars()

    volume_mount = build_volume_mount()
    volume_mounts = [volume_mount]

    sidecar_container = build_container(env_vars, volume_mounts)

    pod.spec.containers.append(sidecar_container)
    pod.spec.share_process_namespace = True  # In order to share the PID namespace of the main container with the sidecar container.

    hostpath_volume = build_hostpath_volume()
    pod.spec.volumes = pod.spec.volumes or []
    pod.spec.volumes.append(hostpath_volume)

    recreate_pod(pod_name, pod_namespace, pod.metadata, pod.spec)
