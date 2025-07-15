from kubernetes import client, config

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()
app_v1 = client.AppsV1Api()
custom_obj_api = client.CustomObjectsApi()
