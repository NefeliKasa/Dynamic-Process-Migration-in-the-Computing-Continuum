from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import custom_obj_api
from k8s_utils.edge_nodes.constants import API_VERSION, KIND, GROUP, VERSION, PLURAL


def create_edge_node(
    edge_node_group,
    cpu_usage_threshold,
    ram_usage_threshold,
    monitoring_interval,
    cpu_observation_interval,
    restore_policy,
):
    edge_node = {
        "apiVersion": API_VERSION,
        "kind": KIND,
        "metadata": {"name": edge_node_group},
        "spec": {
            "cpuUsageThreshold": cpu_usage_threshold,
            "ramUsageThreshold": ram_usage_threshold,
            "monitoringInterval": monitoring_interval,
            "cpuObservationInterval": cpu_observation_interval,
            "restorePolicy": restore_policy,
        },
    }

    safe_kube_call(
        custom_obj_api.create_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=PLURAL,
        body=edge_node,
    )
