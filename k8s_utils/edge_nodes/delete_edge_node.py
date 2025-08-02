from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import custom_obj_api
from k8s_utils.edge_nodes.constants import GROUP, VERSION, PLURAL


def delete_edge_node(edge_node_name):
    safe_kube_call(
        custom_obj_api.delete_cluster_custom_object,
        group=GROUP,
        version=VERSION,
        plural=PLURAL,
        name=edge_node_name,
    )
