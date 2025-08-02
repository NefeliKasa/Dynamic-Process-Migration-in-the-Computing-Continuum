from kubernetes import client
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import batch_v1
from k8s_utils.pods.pod_info import get_node_name
from utils.logging_config import setup_logger
from config import (
    CPU_USAGE_THRESHOLD,
    RAM_USAGE_THRESHOLD,
    MONITORING_INTERVAL,
    CPU_OBSERVATION_INTERVAL,
    RESTORE_POLICY,
    RCN_NAME,
    NAMESPACE,
)
from constants import (
    SIDECAR_CONTROLLER_LABEL,
    SIDECAR_CONTROLLER_IMAGE,
    SIDECAR_CONTROLLER_SERVICE_ACCOUNT_NAME,
    CHECKPOINT_VOLUME_PATH,
    CHECKPOINT_MOUNT_PATH,
)


def build_env_vars(pod_name, pod_namespace, container_name, id):
    return [
        client.V1EnvVar(name="CPU_USAGE_THRESHOLD", value=CPU_USAGE_THRESHOLD),
        client.V1EnvVar(name="RAM_USAGE_THRESHOLD", value=RAM_USAGE_THRESHOLD),
        client.V1EnvVar(name="MONITORING_INTERVAL", value=MONITORING_INTERVAL),
        client.V1EnvVar(
            name="CPU_OBSERVATION_INTERVAL", value=CPU_OBSERVATION_INTERVAL
        ),
        client.V1EnvVar(name="RCN_NAME", value=RCN_NAME),
        client.V1EnvVar(name="RESTORE_POLICY", value=RESTORE_POLICY),
        client.V1EnvVar(name="POD_NAME", value=pod_name),
        client.V1EnvVar(name="POD_NAMESPACE", value=pod_namespace),
        client.V1EnvVar(name="CONTAINER_NAME", value=container_name),
        client.V1EnvVar(name="CHECKPOINTS_DIR_PATH", value=CHECKPOINT_MOUNT_PATH),
    ]


def build_volume_mounts():
    return [
        client.V1VolumeMount(name="checkpoint-dir", mount_path=CHECKPOINT_MOUNT_PATH)
    ]


def build_container(env_vars, volume_mounts, security_context):
    return client.V1Container(
        name="sidecar-controller-container",
        image=SIDECAR_CONTROLLER_IMAGE,
        env=env_vars,
        volume_mounts=volume_mounts,
        security_context=security_context,
        image_pull_policy="Always",
    )


def build_volumes():
    host_path = client.V1HostPathVolumeSource(
        path=CHECKPOINT_VOLUME_PATH, type="DirectoryOrCreate"
    )

    volume = client.V1Volume(name="checkpoint-dir", host_path=host_path)
    return [volume]


def build_pod_template(node_name, containers, volumes):
    metadata = client.V1ObjectMeta(labels={"app": SIDECAR_CONTROLLER_LABEL})

    spec = client.V1PodSpec(
        node_name=node_name,
        service_account_name=SIDECAR_CONTROLLER_SERVICE_ACCOUNT_NAME,
        containers=containers,
        volumes=volumes,
        restart_policy="Never",
    )

    return client.V1PodTemplateSpec(metadata=metadata, spec=spec)


def build_job(pod_name, template):
    name = f"{RCN_NAME}-sidecar-controller-{pod_name}"
    metadata = client.V1ObjectMeta(name=name)

    spec = client.V1JobSpec(
        template=template, backoff_limit=0, ttl_seconds_after_finished=120
    )

    return client.V1Job(metadata=metadata, spec=spec)


def create_sidecar_controller(pod_name, pod_namespace, container_name):
    # For each pod, a custom sidecar controller handler is deployed.
    env_vars = build_env_vars(pod_name, pod_namespace, container_name, id)
    volume_mounts = build_volume_mounts()
    security_context = client.V1SecurityContext(
        privileged=True
    )  # In order to run buildah
    container = build_container(env_vars, volume_mounts, security_context)

    containers = [container]
    volumes = build_volumes()
    NODE_NAME = get_node_name(
        pod_name, pod_namespace
    )  # The sidecar controller needs to be deployed in the same node as the pod, in order to access info from the host filesystem (such as cgroups) and use the checkpoint API.
    template = build_pod_template(NODE_NAME, containers, volumes)

    job = build_job(pod_name, template)

    safe_kube_call(
        batch_v1.create_namespaced_job,
        namespace=NAMESPACE,
        body=job,
        ignore_conflict=True,
    )
