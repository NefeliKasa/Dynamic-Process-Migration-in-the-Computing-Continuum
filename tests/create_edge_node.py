from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import custom_obj_api
from constants import GROUP, VERSION, PLURAL


def create_edge_node_cr():
    # We add a new EdgeNode custom resource, in order to test our orchestration setup.
    edge_node = {
        "apiVersion": "criu.thesis/v1",
        "kind": "EdgeNode",
        "metadata": {"name": "eks-edge"},
        "spec": {
            "cpuUsageThreshold": 90,
            "ramUsageThreshold": 90,
            "monitoringInterval": 1,
            "cpuObservationInterval": 1,
            "offloadPolicy": "reactive",
            "restorePolicy": "restart",
        },
    }

    safe_kube_call(
        custom_obj_api.create_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=PLURAL,
        body=edge_node,
    )
