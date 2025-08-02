from kubernetes import client
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import app_v1
from config import NAMESPACE
from constants import (
    POD_CONTROLLER_LABEL,
    POD_CONTROLLER_IMAGE,
    POD_CONTROLLER_SERVICE_ACCOUNT_NAME,
    POD_CONTROLLER_LAYER,
)


def get_rcn_info(rcn):
    metadata = rcn["metadata"]
    RCN_NAME = metadata["name"]

    spec = rcn["spec"]
    cpu_usage_threshold = spec["cpuUsageThreshold"]
    ram_usage_threshold = spec["ramUsageThreshold"]
    monitoring_interval = spec["monitoringInterval"]
    cpu_observation_interval = spec["cpuObservationInterval"]
    restore_policy = spec["restorePolicy"]

    return (
        RCN_NAME,
        cpu_usage_threshold,
        ram_usage_threshold,
        monitoring_interval,
        cpu_observation_interval,
        restore_policy,
    )


def build_env_vars(rcn):
    (
        RCN_NAME,
        cpu_usage_threshold,
        ram_usage_threshold,
        monitoring_interval,
        cpu_observation_interval,
        restore_policy,
    ) = get_rcn_info(rcn)

    env_vars = [
        client.V1EnvVar(name="RCN_NAME", value=RCN_NAME),
        client.V1EnvVar(name="CPU_USAGE_THRESHOLD", value=str(cpu_usage_threshold)),
        client.V1EnvVar(name="RAM_USAGE_THRESHOLD", value=str(ram_usage_threshold)),
        client.V1EnvVar(name="MONITORING_INTERVAL", value=str(monitoring_interval)),
        client.V1EnvVar(
            name="CPU_OBSERVATION_INTERVAL", value=str(cpu_observation_interval)
        ),
        client.V1EnvVar(name="RESTORE_POLICY", value=restore_policy),
        client.V1EnvVar(name="SETUP_NAMESPACE", value=NAMESPACE),
    ]

    return env_vars


def build_container(env_vars):
    global container_name
    container_name = "pod-controller-container"

    return client.V1Container(
        name=container_name,
        image=POD_CONTROLLER_IMAGE,
        env=env_vars,
        image_pull_policy="Always",
    )


def build_pod_template(containers):
    metadata = client.V1ObjectMeta(labels={"app": POD_CONTROLLER_LABEL})
    spec = client.V1PodSpec(
        service_account_name=POD_CONTROLLER_SERVICE_ACCOUNT_NAME,
        containers=containers,
        node_selector={"layer": POD_CONTROLLER_LAYER},
    )

    return client.V1PodTemplateSpec(metadata=metadata, spec=spec)


def build_deployment(rcn_name, template):
    global deployment_name
    deployment_name = f"{rcn_name}-pod-controller"
    metadata = client.V1ObjectMeta(name=deployment_name)

    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": POD_CONTROLLER_LABEL}),
        template=template,
    )

    return client.V1Deployment(metadata=metadata, spec=spec)


def create_pod_controller(rcn):
    # Every time a new EdgeNode is created, we deploy a pod watcher for pods running in the node.

    # We gather information from the rcn that needs to be passed down to the pod controller.
    env_vars = build_env_vars(rcn)

    container = build_container(env_vars)

    containers = [container]
    template = build_pod_template(containers)

    rcn_name = rcn["metadata"]["name"]
    deployment = build_deployment(rcn_name, template)

    safe_kube_call(
        app_v1.create_namespaced_deployment,
        namespace=NAMESPACE,
        body=deployment,
        ignore_conflict=True,
    )


def build_patch(env_vars):
    return {
        "spec": {
            "template": {
                "spec": {"containers": [{"name": container_name, "env": env_vars}]}
            }
        }
    }


def patch_pod_controller(rcn):
    # Every time an EdgeNode is updated, the enviroment variables of the pod controller deployment are updated as well.
    env_vars = build_env_vars(rcn)

    patch = build_patch(env_vars)

    safe_kube_call(
        app_v1.patch_namespaced_deployment,
        name=deployment_name,
        namespace=NAMESPACE,
        body=patch,
    )

    return


def delete_pod_controller(rcn):
    safe_kube_call(
        app_v1.delete_namespaced_deployment,
        name=deployment_name,
        namespace=NAMESPACE,
        propagation_policy="Foreground",
        ignore_not_found=True,
    )
