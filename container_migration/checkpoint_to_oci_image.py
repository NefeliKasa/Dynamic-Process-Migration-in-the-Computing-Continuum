import os
import subprocess
import re
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def find_checkpoint_tar(pod_name, pod_namespace, container_name, checkpoints_dir_path):
    pattern = re.compile(
        rf"^checkpoint-{pod_name}_{pod_namespace}-{container_name}-\d+\.tar$"
    )

    for root, _, files in os.walk(checkpoints_dir_path):
        for file in files:
            if pattern.match(file):
                return os.path.join(root, file)

    logger.error(f"checkpoint-{pod_name}_{pod_namespace}-{container_name} not found.")
    raise RuntimeError


def run_command(cmd, command_name):
    try:
        subprocess.run(cmd, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command {command_name} failed: {e}")
        raise RuntimeError


def transform_checkpoint_to_oci_image(
    pod_name, pod_namespace, container_name, checkpoints_dir_path, new_image_name
):
    try:
        cmd = ["buildah", "from", "scratch"]
        new_container = subprocess.check_output(cmd, text=True, check=True).strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command buildah from scratch failed: {e}")
        raise RuntimeError

    CONTAINER_CHECKPOINT_PATH = find_checkpoint_tar(
        pod_name, pod_namespace, container_name, checkpoints_dir_path
    )

    run_command(
        ["buildah", "add", new_container, checkpoints_dir_path, "/"],
        "buildah add",
    )

    run_command(
        [
            "buildah",
            "config",
            f"--annotation=io.kubernetes.cri-o.annotations.checkpoint.name={container_name}",
            new_container,
        ],
        "buildah config",
    )

    run_command(
        ["buildah", "commit", new_container, f"{new_image_name}:latest"],
        "buildah commit",
    )

    run_command(["buildah", "rm", new_container], "buildah rm")

    registry = "docker.io"
    username = "nefks"
    password = "BeforeSunrise4969*"
    run_command(
        ["buildah", "login", "-u", username, "-p", password, registry],
        "buildah login",
    )

    remote_image = f"{registry}/{username}/{new_image_name}:latest"
    run_command(
        ["buildah", "tag", f"{new_image_name}:latest", remote_image],
        "Command buildah tag failed:",
    )

    run_command(["buildah", "push", remote_image], "buildah push")

    try:
        os.remove(CONTAINER_CHECKPOINT_PATH)
    except OSError as e:
        logger.error(f"Error deleting checkpoint file {CONTAINER_CHECKPOINT_PATH}: {e}")
        raise RuntimeError
