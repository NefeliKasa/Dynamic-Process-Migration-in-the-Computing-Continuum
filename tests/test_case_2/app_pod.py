from kubernetes import client
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1


def create_app_pod(
    app_pod_name, app_pod_layer, app_pod_node_group, application_image, namespace
):
    pod_metadata = client.V1ObjectMeta(
        name=app_pod_name,
    )

    container = client.V1Container(
        name=f"{app_pod_name}-container",
        image=application_image,
    )

    pod_spec = client.V1PodSpec(
        containers=[container],
        restart_policy="OnFailure",
        node_selector={"layer": app_pod_layer, "node-group": app_pod_node_group},
    )

    pod = client.V1Pod(
        metadata=pod_metadata,
        spec=pod_spec,
    )

    safe_kube_call(v1.create_namespaced_pod, namespace=namespace, body=pod)


def delete_app_pod(app_pod_name, namespace):
    safe_kube_call(
        v1.delete_namespaced_pod,
        name=app_pod_name,
        namespace=namespace,
        ignore_not_found=True,
    )
