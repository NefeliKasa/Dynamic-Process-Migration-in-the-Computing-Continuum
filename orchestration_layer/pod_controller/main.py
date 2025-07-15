from signals import init_sigterm_handler
from watcher import watch_pods


def main():
    init_sigterm_handler()

    watch_pods()


if __name__ == "__main__":
    main()
