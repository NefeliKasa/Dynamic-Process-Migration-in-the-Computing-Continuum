SIDECAR_CONTROLLER_LABEL = "sidecar-controller"
POD_CONTROLLER_LABEL = "pod-controller"
RCN_CONTROLLER_LABEL = "rcn-controller"
CHECKPOINT_LABEL = "checkpoint"

EXCLUDED_APPS = {
    RCN_CONTROLLER_LABEL,
    POD_CONTROLLER_LABEL,
    SIDECAR_CONTROLLER_LABEL,
}

SIDECAR_CONTROLLER_IMAGE = "nefks/sidecar_controller:latest"
SIDECAR_CONTROLLER_SERVICE_ACCOUNT_NAME = "sidecar-controller"

CHECKPOINT_VOLUME_PATH = "/var/lib/kubelet/checkpoints/"
CHECKPOINT_MOUNT_PATH = "/mnt/checkpoints"
