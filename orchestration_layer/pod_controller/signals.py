import signal

sigterm_received = False


def sigterm_handler(signum, frame):
    global sigterm_received
    sigterm_received = True


def init_sigterm_handler():
    signal.signal(signal.SIGTERM, sigterm_handler)
