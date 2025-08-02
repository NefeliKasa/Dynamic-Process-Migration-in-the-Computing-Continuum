from utils.logging_config import setup_logger
from k8s_utils.edge_nodes.create_edge_node import create_edge_node
from k8s_utils.edge_nodes.delete_edge_node import delete_edge_node
from k8s_utils.deployments.wait_for_deployment_ready import wait_for_deployment_ready
from k8s_utils.jobs.wait_for_job_event import (
    wait_for_job_creation,
    wait_for_job_termination,
)
from tests.test_case_2.app_pod import create_app_pod, delete_app_pod
from tests.config import EDGE_NODE_GROUP, SETUP_NAMESPACE
from constants import (
    CPU_USAGE_THRESHOLD,
    RAM_USAGE_THRESHOLD,
    MONITORING_INTERVAL,
    CPU_OBSERVATION_INTERVAL,
    RESTORE_POLICY,
    APP_POD_NAME,
    APP_POD_LAYER,
    APPLICATION_IMAGE,
    POD_CONTROLLER_DEPLOYMENT_NAME,
    SIDECAR_CONTROLLER_JOB_NAME,
)

logger = setup_logger(__name__)


def main():

    create_edge_node(
        EDGE_NODE_GROUP,
        CPU_USAGE_THRESHOLD,
        RAM_USAGE_THRESHOLD,
        MONITORING_INTERVAL,
        CPU_OBSERVATION_INTERVAL,
        RESTORE_POLICY,
    )
    logger.info("EdgeNode custom resource created successfully.")

    wait_for_deployment_ready(POD_CONTROLLER_DEPLOYMENT_NAME, SETUP_NAMESPACE)

    create_app_pod(
        APP_POD_NAME, APP_POD_LAYER, EDGE_NODE_GROUP, APPLICATION_IMAGE, SETUP_NAMESPACE
    )

    wait_for_job_creation(SIDECAR_CONTROLLER_JOB_NAME, SETUP_NAMESPACE)

    wait_for_job_termination(SIDECAR_CONTROLLER_JOB_NAME, SETUP_NAMESPACE, timeout=600)

    delete_app_pod(APP_POD_NAME, SETUP_NAMESPACE)

    delete_edge_node(EDGE_NODE_GROUP)


if __name__ == "__main__":
    main()
