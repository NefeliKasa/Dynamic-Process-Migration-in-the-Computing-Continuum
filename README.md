# Dynamic Process Migration from Edge to Cloud

This project was developed as part of my undergraduate thesis in the Department of Informatics and Telecommunications at the University of Athens.
Its aim is to develop an automated, multi-level mechanism for monitoring and migrating applications within a simulated edge-cloud environment on a Kubernetes cluster.

## Project Structure

### Orchestration Layer

- **orchestration_layer/rcn_controller/** <br>
  Watches for the creation/update events of EdgeNode custom resources. When a new node is registered, the controller deploys a pod-level watcher (pod_controller) to monitor pods scheduled on that node.

- **orchestration_layer/pod_controller/** <br>
  Watches for pod creation events and deploys a custom sidecar controller for each pod.

- **orchestration_layer/sidecar_controller/** <br>
  Injects a monitoring sidecar into each pod. Receives resource usage metrics from the sidecar and deploys a checkpointing mechanism when thresholds are exceeded.

- **orchestration_layer/monitor/** <br> 
  A sidecar process that monitors the CPU and RAM usage of the main container app.

### Container Migration
- **container_migration/checkpoint_container.py** <br>
  Module that performs container checkpointing.
- **container_migration/checkpoint_to_oci_image.py** <br>
  Module that performs transformation of a checkpoint directory to an OCI image.
- **container_migration/restore_container_in_cloud.py** <br>
  Module that performs restoration of a container to the cloud layer.
- **container_migration/migrate_running_container.py** <br>
  Module that performs a container migration from edge to cloud, utilizing the files described above. 


### Utilities
- **utils/logging_config.py** <br>
  Logging configuration used across the entire setup.


### Kubernetes Utilities
- **k8s_utils/kube_init.py** <br>
  Configuration of Kubernetes API and initialization of API instances.
- **k8s_utils/safe_kube_call.py** <br>
  Kubernetes API call wrapper that handles exceptions and performs retries.
- **k8s_utils/pod_cleanup.py** <br>
  Functions used to assist cleanup-related activities in pods.
- **k8s_utils/pod_info.py** <br>
  Functions used to assist information retrieval activities in pods.
- **k8s_utils/pod_recreation.py** <br>
  Functions used to assist in pod recreation.


### Kubernetes Configurations
- **k8s/service_accounts/** <br> 
  Service accounts and RBAC settings for controller permissions.

- **k8s/config_maps/** <br> 
  Shared configurations used across orchestration components.

- **k8s/pods/** <br> 
  Pod manifests for the pod controller and the test app.

- **k8s/jobs/** <br> 
  Job manifests for the pod controller and the test app.

- **k8s/deployments/** <br>
  Deployment manifests for the pod controller and the test app.

### Nats
- **nats_prod** <br>
  High level wrapper for the nats python client.

### Application
- **app/image_reduction/** <br>
  A neural network image reduction application used to simulate load and validate orchestration behavior.

### Tests
This directory contains tests deployed to assess the functionality of the entire setup.
