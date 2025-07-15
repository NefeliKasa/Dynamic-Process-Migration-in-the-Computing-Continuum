import psutil
from datetime import datetime


def get_cpu_usage(interval=1):
    return psutil.cpu_percent(interval)


def get_ram_usage():
    return psutil.virtual_memory().percent


def build_metrics_message(cpu_interval):
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": get_cpu_usage(cpu_interval),
        "ram_usage": get_ram_usage(),
    }
