from kubernetes import client
from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1
from k8s_utils.pods.pod_cleanup import wait_for_pod_termination


def remove_metadata_runtime_fields(pod_metadata):
    pod_metadata.resource_version = None
    pod_metadata.uid = None
    pod_metadata.self_link = None
    pod_metadata.creation_timestamp = None
    pod_metadata.managed_fields = None
    pod_metadata.owner_references = None


def remove_spec_runtime_fields(pod_spec):
    pod_spec.node_name = None


def recreate_pod(pod_name, pod_namespace, pod_metadata, pod_spec, is_deleted=False):
    if not is_deleted:
        safe_kube_call(v1.delete_namespaced_pod, name=pod_name, namespace=pod_namespace)

    remove_metadata_runtime_fields(pod_metadata)
    remove_spec_runtime_fields(pod_spec)

    if pod_metadata.labels is None:
        pod_metadata.labels = {}
    pod_metadata.labels["recreated"] = "yes"

    recreated_pod = client.V1Pod(metadata=pod_metadata, spec=pod_spec)

    wait_for_pod_termination(pod_name, pod_namespace)

    safe_kube_call(
        v1.create_namespaced_pod, namespace=pod_namespace, body=recreated_pod
    )
