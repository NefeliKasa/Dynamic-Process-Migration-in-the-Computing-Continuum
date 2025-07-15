from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1


def get_pod_data(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return (pod.metadata, pod.spec)


def get_container_in_pod(pod_spec, container_name):
    for i, container in enumerate(pod_spec.containers):
        if container.name != container_name:
            continue
        else:
            return container


def get_node_name(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return pod.spec.node_name


def get_node_ip(pod_name, pod_namespace):
    pod = safe_kube_call(v1.read_namespaced_pod, name=pod_name, namespace=pod_namespace)

    return pod.status.host_ip
