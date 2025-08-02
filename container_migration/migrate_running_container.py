from utils.logging_config import setup_logger
from k8s_utils.pods.pod_info import get_pod_data, get_container_in_pod
from container_migration.checkpoint_container import checkpoint_container
from container_migration.checkpoint_to_oci_image import (
    transform_checkpoint_to_oci_image,
)
from container_migration.restore_container_in_cloud import restore_container_in_cloud

logger = setup_logger(__name__)


def migrate_running_container(
    pod_name, pod_namespace, container_name, restore_policy, checkpoints_dir_path=None
):
    # In case a edge node resource exhaustion, a migration routine is initiated.

    pod_metadata, pod_spec = get_pod_data(pod_name, pod_namespace)
    container = get_container_in_pod(pod_spec, container_name)
    IMAGE_NAME = container.image

    # In the checkpoint method, the running container is checkpointed
    # and a new OCI image is built from the checkpoint directory contents.
    # A new pod resumes execution for the checkpoint image in the cloud node.
    if restore_policy == "checkpoint":
        checkpoint_container(pod_name, pod_namespace, container_name)

        CHECKPOINT_IMAGE_NAME = f"{IMAGE_NAME}-checkpoint"
        transform_checkpoint_to_oci_image(
            pod_name,
            pod_namespace,
            container_name,
            checkpoints_dir_path,
            CHECKPOINT_IMAGE_NAME,
        )

        restore_container_in_cloud(
            pod_metadata,
            pod_spec,
            container_name,
            CHECKPOINT_IMAGE_NAME,
            is_deleted=True,
        )
    # In the restart method, the container is restarted in the cloud node.
    elif restore_policy == "restart":
        restore_container_in_cloud(pod_metadata, pod_spec, container_name, IMAGE_NAME)
    else:
        logger.error(
            f"Invalid restore policy: {restore_policy}. "
            "Expected 'checkpoint' or 'restart'."
        )

    logger.info(
        f"Migration completed for container {container_name} in pod {pod_name}."
    )
