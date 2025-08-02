from config import RCN_NAME, POD_NAME

MONITOR_IMAGE = "nefks/monitor:latest"
SERVICE_ACCOUNT_NAME = "sidecar"

MONITORING_TOPIC = f"{RCN_NAME}-{POD_NAME}-monitoring"

HOST_POD_METRICS_PATH = "/sys/fs/cgroup/kubepods.slice"
HOST_POD_METRICS_MOUNT_PATH = "/host_metrics"
