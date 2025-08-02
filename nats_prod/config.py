from k8s_utils.general.safe_kube_call import safe_kube_call
from k8s_utils.general.kube_init import v1

config_map = safe_kube_call(
    v1.read_namespaced_config_map, name="nats-config", namespace="nats"
)
NATS_URL = config_map.data.get("NATS_URL", "nats://nats.nats.svc.cluster.local:4222")
