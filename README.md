# Dynamic Process Migration from Edge to Cloud

This project was developed as part of my undergraduate thesis in the Department of Informatics and Telecommunications at the University of Athens.
Its aim is to develop an automated, multi-level mechanism for monitoring and migrating applications within a simulated edge-cloud environment on a Kubernetes cluster.

## Project Structure
The code of this thesis is separated into the following modular directories:

### orchestration_layer
This directory contains all the orchestration components of the proposed migration system.

- **orchestration_layer/rcn_controller/** <br>
  Watches for the creation/update events of EdgeNode custom resources. When a new node is registered, the controller deploys a pod-level watcher (pod_controller) to monitor pods scheduled on that node.

- **orchestration_layer/pod_controller/** <br>
  Watches for pod creation events and deploys a custom sidecar controller for each pod.

- **orchestration_layer/sidecar_controller/** <br>
  Injects a monitoring sidecar into each pod. Receives resource usage metrics from the sidecar and deploys a checkpointing mechanism when thresholds are exceeded.

- **orchestration_layer/monitor/** <br> 
  A sidecar process that monitors the CPU and RAM usage of the main container app.

### container_migration
This directory contains functions for the various migration methods used.

- **container_migration/checkpoint_container.py** <br>
  Module that performs container checkpointing.
- **container_migration/checkpoint_to_oci_image.py** <br>
  Module that performs transformation of a checkpoint directory to an OCI image.
- **container_migration/restore_container_in_cloud.py** <br>
  Module that performs restoration of a container to the cloud layer.
- **container_migration/migrate_running_container.py** <br>
  Module that performs a container migration from edge to cloud, utilizing the files described above. 


### utilities
This directory contains general utility functions. 

- **utils/logging_config.py** <br>
  Logging configuration used across the entire setup.


### k8s_utilities
This directory contains Kubernetes utility functions for custom and core resources.  

- **k8s_utils/general/** <br>
  General purpose Kubernetes functions that don't apply to a specific resource type.
- **k8s_utils/pods/** <br>
  Kubernetes functions that offer utilities for pod resources.
- **k8s_utils/deployments/** <br>
  Kubernetes functions that offer utilities for deployment resources.
- **k8s_utils/jobs/** <br>
  Kubernetes functions that offer utilities for job resources.
- **k8s_utils/edge_nodes/** <br>
  Kubernetes functions that offer utilities for edge node custom resources.


### k8s
This directory contains all the configuration files of Kubernetes resources that are manually deployed in the cluster.

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

### nats
This directory contains high-level functions that utilize the NATS messaging system. 

- **nats_prod/** <br>
  High-level wrapper for the nats python client.

### app
This directory contains an application used in the setup tests. 

- **app/image_reduction/** <br>
  A neural network image reduction application used to simulate load and validate orchestration behavior.

### tests
This directory contains tests deployed to assess the functionality of the entire setup.

- **tests/test_case_1/** <br>
  Test case using the image reduction app and the restart restore policy.  
- **tests/test_case_2/** <br>
  Test case using the image reduction app and the checkpoint restore policy.  
- **tests/test_case_3/** <br>
  Test case using the image reduction app with a CPU core limit and the restart restore policy.  

### system_demo
This directory contains screenshots of the system's state during test case execution. The screenshots were taken from the Lens Kubernetes GUI, using the nodes from our AWS EKS cluster. 

- **system_demo/test_case_1/** <br>
  Screenshots from the test case 1 execution. 
- **system_demo/test_case_2/** <br>
  Screenshots from the test case 2 execution. 
- **system_demo/test_case_3/** <br>
  Screenshots from the test case 3 execution.  

## Build Commands
The build commands for creating all the docker images used to build and test the proposed system are found below:  

- docker buildx build -f orchestration_layer/rcn_controller/Dockerfile -t nefks/rcn_controller:latest --platform linux/arm64 --push .

- docker buildx build -f orchestration_layer/pod_controller/Dockerfile -t nefks/pod_controller:latest --platform linux/arm64 --push .

- docker buildx build -f orchestration_layer/sidecar_controller/Dockerfile -t nefks/sidecar_controller:latest --platform linux/arm64 --push .

- docker buildx build -f orchestration_layer/monitor/Dockerfile -t nefks/monitor:latest --platform linux/arm64 --push .

- docker buildx build -f tests/test_case_1/Dockerfile -t nefks/criu_test_case_1:latest --platform linux/arm64 --push .

- docker buildx build -f tests/test_case_2/Dockerfile -t nefks/criu_test_case_2:latest --platform linux/arm64 --push .
  
- docker buildx build -f tests/test_case_3/Dockerfile -t nefks/criu_test_case_3:latest --platform linux/arm64 --push .
