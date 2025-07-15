from utils.logging_config import setup_logger
from create_edge_node import create_edge_node_cr

logger = setup_logger(__name__)


def main():
    create_edge_node_cr()
    logger.info("EdgeNode custom resource created successfully.")


if __name__ == "__main__":
    main()
