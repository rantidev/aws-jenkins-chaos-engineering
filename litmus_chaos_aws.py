#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import random
import os
import sys
from requests.auth import HTTPDigestAuth

LITMUS_URL = ''
LITMUS_USERNAME = ''
LITMUS_PASSWORD = ''
LITMUS_PROJECT_ID = ''
MONGODB_ATLAS_PUBLIC_KEY = ''
MONGODB_ATLAS_PRIVATE_KEY = ''
LITMUS_PROJECT_ID = ''
test_result_dict = {}
global_config_data = ''
running_workflow_details = ''
probe_url = ''
experiment_type = ''
config_data_res = ''


def get_auth_token():
    cred_data = {'username': LITMUS_USERNAME,
                 'password': LITMUS_PASSWORD}
    response = requests.post(LITMUS_URL + '/auth/login',
                             json.dumps(cred_data))
    return response


############################################################################################################
def get_cluster_id():
    response = get_auth_token()
    print('RESPONSE : ' , response)

    access_token = response.json()['access_token']

    headers = {'authorization': access_token, 'Content-type': 'application/json'}
    data = {
      "operationName": "listClusters",
      "variables": {
        "projectID": LITMUS_PROJECT_ID
      },
      "query": "query listClusters($projectID: String!) {\n  listClusters(projectID: $projectID) {\n    clusterID\n    __typename\n  }\n}\n"
    }
    
    response = requests.post(LITMUS_URL + '/api/query', data=json.dumps(data), headers=headers)
    cluster_id = response.json()['data']['listClusters'][0]['clusterID']
    return cluster_id


##########################################################################################################
def execute_pod_kill_experiment():
    pod_delete = config_data_res['pod_delete']
    pod_delete_namespace = pod_delete['eks_ns']
    pod_delete_deployment = pod_delete['eks_pod']
    pod_delete_env = pod_delete['env']

    response = get_auth_token()

    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}

    workflow_name = 'pod-kill-workflow-' + get_random_number()
    json_data = get_pod_kill_request_body(workflow_name, pod_delete_namespace, pod_delete_deployment)

    pod_kill_response = requests.post(LITMUS_URL + '/api/query', data=json_data, headers=headers)
    print(pod_kill_response.json())
    print(pod_kill_response.status_code)


########################################################################################################33

def get_pod_kill_request_body(workflow_name, namespace, deployment):
    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID
    isCustomWorkflow = bool(True)

    data = {
      "operationName": "createChaosWorkFlow",
      "variables": {
          "request": {
              "workflowManifest": "{\n  \"apiVersion\": \"argoproj.io/v1alpha1\",\n  \"kind\": \"Workflow\",\n  \"metadata\": {\n    \"name\": \"updated_workflow_name\",\n    \"namespace\": \"litmus\",\n    \"labels\": {\n      \"subject\": \"custom-chaos-workflow_litmus\"\n    }\n  },\n  \"spec\": {\n    \"arguments\": {\n      \"parameters\": [\n        {\n          \"name\": \"adminModeNamespace\",\n          \"value\": \"litmus\"\n        }\n      ]\n    },\n    \"entrypoint\": \"custom-chaos\",\n    \"securityContext\": {\n      \"runAsNonRoot\": true,\n      \"runAsUser\": 1000\n    },\n    \"serviceAccountName\": \"argo-chaos\",\n    \"templates\": [\n      {\n        \"name\": \"custom-chaos\",\n        \"steps\": [\n          [\n            {\n              \"name\": \"install-chaos-experiments\",\n              \"template\": \"install-chaos-experiments\"\n            }\n          ],\n          [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"template\": \"pod-delete-zqn\"\n            }\n          ],\n          [\n            {\n              \"name\": \"revert-chaos\",\n              \"template\": \"revert-chaos\"\n            }\n          ]\n        ]\n      },\n      {\n        \"name\": \"install-chaos-experiments\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"path\": \"/tmp/pod-delete-zqn.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Deletes a pod belonging to a deployment/statefulset/daemonset\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-delete\\n  labels:\\n    name: pod-delete\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: 2.9.0\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: litmuschaos/go-runner:2.9.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-delete\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\\"total_chaos_duration\\\"\\n      - name: RAMP_TIME\\n        value: \\\"\\\"\\n      - name: FORCE\\n        value: \\\"true\\\"\\n      - name: CHAOS_INTERVAL\\n        value: \\\"60\\\"\\n      - name: PODS_AFFECTED_PERC\\n        value: \\\"pods_affected_percentage\\\"\\n      - name: LIB\\n        value: litmus\\n      - name: TARGET_PODS\\n        value: \\\"\\\"\\n      - name: NODE_LABEL\\n        value: \\\"\\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-delete\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/version: 2.9.0\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"kubectl apply -f /tmp/pod-delete-zqn.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30\"\n          ],\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"image\": \"litmuschaos/k8s:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"pod-delete-zqn\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"path\": \"/tmp/chaosengine-pod-delete-zqn.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\\"{{workflow.parameters.adminModeNamespace}}\\\"\\n  generateName: pod-delete-zqn\\n  labels:\\n    instance_id: 0a88efa2-c9fd-4342-ac9d-261e8303d079\\n    workflow_name: updated_workflow_name\\nspec:\\n  appinfo:\\n    appns: updated_namespace\\n    applabel: app=app_name\\n    appkind: deployment\\n  engineState: active\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-delete\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\\"total_chaos_duration\\\"\\n            - name: CHAOS_INTERVAL\\n              value: \\\"chaos_interval\\\"\\n            - name: FORCE\\n              value: \\\"false\\\"\\n            - name: PODS_AFFECTED_PERC\\n              value: \\\"pods_affected_percentage\\\"\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"-file=/tmp/chaosengine-pod-delete-zqn.yaml\",\n            \"-saveName=/tmp/engine-name\"\n          ],\n          \"image\": \"litmuschaos/litmus-checker:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"revert-chaos\",\n        \"container\": {\n          \"image\": \"litmuschaos/k8s:2.9.0\",\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"args\": [\n            \"kubectl delete chaosengine -l 'instance_id in (0a88efa2-c9fd-4342-ac9d-261e8303d079, )' -n {{workflow.parameters.adminModeNamespace}} \"\n          ]\n        }\n      }\n    ],\n    \"podGC\": {\n      \"strategy\": \"OnWorkflowCompletion\"\n    }\n  }\n}",
              "cronSyntax": "",
              "workflowName": "updated_workflow_name",
              "workflowDescription": "Custom Chaos Workflow",
              "isCustomWorkflow": isCustomWorkflow,
              "weightages": [
                  {
                      "experimentName": "pod-delete-zqn",
                      "weightage": 10
                  }
              ],
              'projectID': 'updated_project_id',
              'clusterID': 'updated_cluster_id',
          }
      },
      "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
    }

    # replacing values
    updated_workflow_manifest_str = data['variables']['request']['workflowManifest'].replace(
        'updated_workflow_name', workflow_name).replace('updated_namespace', namespace).replace('updated_deployment',
                                                                                                deployment).replace('total_chaos_duration',TOTAL_CHAOS_DURATION).replace('chaos_interval',CHAOS_INTERVAL).replace('pods_affected_percentage',PODS_AFFECTED_PERCENTAGE).replace('app_name', APP_NAME)
    updated_workflow_name_str = data['variables']['request']['workflowName'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['request']['projectID'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['request']['clusterID'].replace('updated_cluster_id', cluster_id)

    # Inserting updated values
    data['variables']['request']['workflowManifest'] = updated_workflow_manifest_str
    data['variables']['request']['workflowName'] = updated_workflow_name_str
    data['variables']['request']['projectID'] = project_id_str
    data['variables']['request']['clusterID'] = cluster_id_str

    print(json.dumps(data))
    return json.dumps(data)


#############################################################################################################
def get_network_latency_experiment_body(workflow_name, namespace, deployment):
    isCustomWorkflow = bool(True)

    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID

    data = {
        "operationName": "createChaosWorkFlow",
        "variables": {
            "request": {
                "workflowManifest": "{\n  \"apiVersion\": \"argoproj.io/v1alpha1\",\n  \"kind\": \"Workflow\",\n  \"metadata\": {\n    \"name\": \"updated_workflow_name\",\n    \"namespace\": \"litmus\",\n    \"labels\": {\n      \"subject\": \"custom-chaos-workflow_litmus\"\n    }\n  },\n  \"spec\": {\n    \"arguments\": {\n      \"parameters\": [\n        {\n          \"name\": \"adminModeNamespace\",\n          \"value\": \"litmus\"\n        }\n      ]\n    },\n    \"entrypoint\": \"custom-chaos\",\n    \"securityContext\": {\n      \"runAsNonRoot\": true,\n      \"runAsUser\": 1000\n    },\n    \"serviceAccountName\": \"argo-chaos\",\n    \"templates\": [\n      {\n        \"name\": \"custom-chaos\",\n        \"steps\": [\n          [\n            {\n              \"name\": \"install-chaos-experiments\",\n              \"template\": \"install-chaos-experiments\"\n            }\n          ],\n          [\n            {\n              \"name\": \"pod-network-latency-okf\",\n              \"template\": \"pod-network-latency-okf\"\n            }\n          ],\n          [\n            {\n              \"name\": \"revert-chaos\",\n              \"template\": \"revert-chaos\"\n            }\n          ]\n        ]\n      },\n      {\n        \"name\": \"install-chaos-experiments\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-network-latency-okf\",\n              \"path\": \"/tmp/pod-network-latency-okf.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Injects network latency on pods belonging to an app deployment\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-network-latency\\n  labels:\\n    name: pod-network-latency\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: 2.9.0\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: litmuschaos/go-runner:2.9.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-network-latency\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TARGET_CONTAINER\\n        value: \\\"\\\"\\n      - name: NETWORK_INTERFACE\\n        value: eth0\\n      - name: LIB_IMAGE\\n        value: litmuschaos/go-runner:2.9.0\\n      - name: TC_IMAGE\\n        value: gaiadocker/iproute2\\n      - name: NETWORK_LATENCY\\n        value: \\\"network_latency\\\"\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\\"total_chaos_duration\\\"\\n      - name: RAMP_TIME\\n        value: \\\"\\\"\\n      - name: JITTER\\n        value: \\\"0\\\"\\n      - name: LIB\\n        value: litmus\\n      - name: PODS_AFFECTED_PERC\\n        value: \\\"pods_affected_percentage\\\"\\n      - name: TARGET_PODS\\n        value: \\\"\\\"\\n      - name: CONTAINER_RUNTIME\\n        value: docker\\n      - name: DESTINATION_IPS\\n        value: \\\"\\\"\\n      - name: DESTINATION_HOSTS\\n        value: \\\"\\\"\\n      - name: SOCKET_PATH\\n        value: /var/run/docker.sock\\n      - name: NODE_LABEL\\n        value: \\\"\\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-network-latency\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/runtime-api-usage: \\\"true\\\"\\n      app.kubernetes.io/version: 2.9.0\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"kubectl apply -f /tmp/pod-network-latency-okf.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30\"\n          ],\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"image\": \"litmuschaos/k8s:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"pod-network-latency-okf\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-network-latency-okf\",\n              \"path\": \"/tmp/chaosengine-pod-network-latency-okf.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\\"{{workflow.parameters.adminModeNamespace}}\\\"\\n  generateName: pod-network-latency-okf\\n  labels:\\n    instance_id: b0b23c16-1adc-46ff-a38d-901e973cd8ad\\n    context: pod-network-latency-okf_litmus\\n    workflow_name: updated_workflow_name\\nspec:\\n  engineState: active\\n  appinfo:\\n    appns: updated_namespace\\n    applabel: app=app_name\\n    appkind: deployment\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-network-latency\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\\"total_chaos_duration\\\"\\n            - name: NETWORK_LATENCY\\n              value: \\\"2000\\\"\\n            - name: JITTER\\n              value: \\\"0\\\"\\n            - name: CONTAINER_RUNTIME\\n              value: docker\\n            - name: SOCKET_PATH\\n              value: /var/run/docker.sock\\n            - name: PODS_AFFECTED_PERC\\n              value: \\\"pods_affected_percentage\\\"\\n        probe: []\\n  annotationCheck: \\\"false\\\"\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"-file=/tmp/chaosengine-pod-network-latency-okf.yaml\",\n            \"-saveName=/tmp/engine-name\"\n          ],\n          \"image\": \"litmuschaos/litmus-checker:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"revert-chaos\",\n        \"container\": {\n          \"image\": \"litmuschaos/k8s:2.9.0\",\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"args\": [\n            \"kubectl delete chaosengine -l 'instance_id in (b0b23c16-1adc-46ff-a38d-901e973cd8ad, )' -n {{workflow.parameters.adminModeNamespace}} \"\n          ]\n        }\n      }\n    ],\n    \"podGC\": {\n      \"strategy\": \"OnWorkflowCompletion\"\n    }\n  }\n}",
                "cronSyntax": "",
                "workflowName": "updated_workflow_name",
                "workflowDescription": "Custom Chaos Workflow",
                "isCustomWorkflow": isCustomWorkflow,
                "weightages": [
                    {
                        "experimentName": "pod-network-latency-okf",
                        "weightage": 10
                    }
                ],
                'projectID': 'updated_project_id',
                'clusterID': 'updated_cluster_id',
            }
        },
        "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
    }

    # replacing values
    updated_workflow_manifest_str = data['variables']['request']['workflowManifest'].replace(
        'updated_workflow_name', workflow_name).replace('updated_namespace', namespace).replace('updated_deployment',
                                                                                                deployment).replace('total_chaos_duration',TOTAL_CHAOS_DURATION_LATENCY).replace('network_latency',NETWORK_LATENCY).replace('pods_affected_percentage',PODS_AFFECTED_PERCENTAGE_LATENCY).replace('app_name', APP_NAME_LATENCY)
    updated_workflow_name_str = data['variables']['request']['workflowName'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['request']['projectID'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['request']['clusterID'].replace('updated_cluster_id', cluster_id)

    # Inserting updated values
    data['variables']['request']['workflowManifest'] = updated_workflow_manifest_str
    data['variables']['request']['workflowName'] = updated_workflow_name_str
    data['variables']['request']['projectID'] = project_id_str
    data['variables']['request']['clusterID'] = cluster_id_str

    print(json.dumps(data))
    return json.dumps(data)


###########################################################################################################
def execute_network_latency_experiment():
    pod_network_slowness = config_data_res['pod_nw_slowness']
    pod_network_slowness_namespace = pod_network_slowness['eks_ns']
    pod_network_slowness_deployment = pod_network_slowness['eks_pod']
    pod_network_slowness_env = pod_network_slowness['env']

    response = get_auth_token()

    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}
    workflow_name = 'network-latency-workflow-' + get_random_number()
    json_data = get_network_latency_experiment_body(workflow_name, pod_network_slowness_namespace,
                                                    pod_network_slowness_deployment)

    net_latency_response = requests.post(LITMUS_URL + '/api/query',
                                         data=json_data, headers=headers)
    print(net_latency_response.status_code)
    print(net_latency_response.json())

###############################################################################################################
def get_ps_custom_experiment_body(workflow_name, experiment_name):

    print('inside get_ps_custom_experiment_body()')

    isCustomWorkflow = bool(True)
    mongo_atlas_cluster_url_value = ''
    mongo_cluster_private_key_value = ''
    mongo_cluster_public_key_value = ''
    kafka_aws_region_value = ''
    kafka_cluster_arn_value = ''
    aws_access_key_id_value = ''
    elastic_cache_node_group_id_value = ''
    elastic_cache_replication_group_id_value = ''
    elastic_cache_aws_region_value = ''
    aws_secret_access_key_value = ''


    if experiment_name == 'ATLAS':
        mongo_atlas_cluster_url_value = mongo_atlas['atlas_url']
        mongo_cluster_private_key_value = mongo_atlas['public_key']
        mongo_cluster_public_key_value = mongo_atlas['private_key']
    elif experiment_name == 'KAFKA':
        kafka_aws_region_value = kafka['kafka_aws_region']
        kafka_cluster_arn_value = kafka['kafka_cluster_arn']
        aws_access_key_id_value = kafka['aws_access_key_id']
        aws_secret_access_key_value = kafka['aws_secret_access_key']
    elif experiment_name == 'REDIS':
        elastic_cache_node_group_id_value = redis['redis_node_groupId']
        elastic_cache_replication_group_id_value = redis['redis_replication_groupId']
        elastic_cache_aws_region_value = redis['redis_aws_region']
        aws_access_key_id_value = redis['aws_access_key_id']
        aws_secret_access_key_value = redis['aws_secret_access_key']
    else:
     print('No custom experiment name supplied')

    custom_experiment_name_value = experiment_name

    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID

    data = {
        "operationName": "createChaosWorkFlow",
        "variables": {
            "request": {
                "workflowManifest": "{\n  \"apiVersion\": \"argoproj.io/v1alpha1\",\n  \"kind\": \"Workflow\",\n  \"metadata\": {\n    \"name\": \"updated_workflow_name\",\n    \"namespace\": \"litmus\",\n    \"labels\": {\n      \"subject\": \"custom-chaos-workflow_litmus\"\n    }\n  },\n  \"spec\": {\n    \"arguments\": {\n      \"parameters\": [\n        {\n          \"name\": \"adminModeNamespace\",\n          \"value\": \"litmus\"\n        }\n      ]\n    },\n    \"entrypoint\": \"custom-chaos\",\n    \"securityContext\": {\n      \"runAsNonRoot\": true,\n      \"runAsUser\": 1000\n    },\n    \"serviceAccountName\": \"argo-chaos\",\n    \"templates\": [\n      {\n        \"name\": \"custom-chaos\",\n        \"steps\": [\n          [\n            {\n              \"name\": \"install-chaos-experiments\",\n              \"template\": \"install-chaos-experiments\"\n            }\n          ],\n          [\n            {\n              \"name\": \"ps-custom-chaos-1ap\",\n              \"template\": \"ps-custom-chaos-1ap\"\n            }\n          ],\n          [\n            {\n              \"name\": \"revert-chaos\",\n              \"template\": \"revert-chaos\"\n            }\n          ]\n        ]\n      },\n      {\n        \"name\": \"install-chaos-experiments\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"ps-custom-chaos-1ap\",\n              \"path\": \"/tmp/ps-custom-chaos-1ap.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: >\\n    it execs inside target pods to run the chaos inject commands, waits for the\\n    chaos duration and reverts the chaos\\nkind: ChaosExperiment\\nmetadata:\\n  name: ps-custom-chaos\\n  labels:\\n    name: ps-custom-chaos\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: latest\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\\"\\\"\\n          - batch\\n          - apps\\n          - litmuschaos.io\\n        resources:\\n          - jobs\\n          - pods\\n          - pods/log\\n          - events\\n          - deployments\\n          - replicasets\\n          - pods/exec\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n          - deletecollection\\n    image: rantidev7/py-runner:custom-chaos-interns-1.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - python3 -u experiment -name chaos\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: ps-custom-chaos\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: ps-custom-chaos-job\\n      app.kubernetes.io/version: latest\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"kubectl apply -f /tmp/ps-custom-chaos-1ap.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30\"\n          ],\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"image\": \"litmuschaos/k8s:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"ps-custom-chaos-1ap\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"ps-custom-chaos-1ap\",\n              \"path\": \"/tmp/chaosengine-ps-custom-chaos-1ap.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  generateName: ps-custom-chaos-1ap\\n  namespace: \\\"{{workflow.parameters.adminModeNamespace}}\\\"\\n  labels:\\n    instance_id: 95c952f9-f530-4910-a6e7-dfb24aa67039\\n    context: ps-custom-chaos-1ap_litmus\\n    workflow_name: updated_workflow_name\\nspec:\\n  engineState: active\\n  auxiliaryAppInfo: \\\"\\\"\\n  chaosServiceAccount: litmus-admin\\n  jobCleanUpPolicy: retain\\n  experiments:\\n    - name: ps-custom-chaos\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\\"10\\\"\\n            - name: AWS_SECRET_ACCESS_KEY\\n              value: AWS_SECRET_ACCESS_KEY_VALUE\\n            - name: AWS_ACCESS_KEY_ID\\n              value: AWS_ACCESS_KEY_ID_VALUE\\n            - name: AWS_ROLE_ARN\\n              value: \\\"\\\"\\n            - name: KAFKA_CLUSTER_ARN\\n              value: KAFKA_CLUSTER_ARN_VALUE\\n            - name: FORCE\\n              value: \\\"true\\\"\\n            - name: KAFKA_AWS_REGION\\n              value: KAFKA_AWS_REGION_VALUE\\n            - name: CUSTOM_EXPERIMENT_NAME\\n              value: CUSTOM_EXPERIMENT_NAME_VALUE\\n            - name: AWS_WEB_IDENTITY_TOKEN_FILE\\n              value: \\\"\\\"\\n            - name: ELASTIC_CACHE_AWS_REGION\\n              value: \\\"ELASTIC_CACHE_AWS_REGION_VALUE\\\"\\n            - name: ELASTIC_CACHE_REPLICATION_GROUP_ID\\n              value: \\\"ELASTIC_CACHE_REPLICATION_GROUP_ID_VALUE\\\"\\n            - name: ELASTIC_CACHE_NODE_GROUP_ID\\n              value: \\\"ELASTIC_CACHE_NODE_GROUP_ID_VALUE\\\"\\n            - name: MONGO_ATLAS_CLUSTER_URL\\n              value: \\\"MONGO_ATLAS_CLUSTER_URL_VALUE\\\"\\n            - name: MONGO_CLUSTER_PUBLIC_KEY\\n              value: \\\"MONGO_CLUSTER_PUBLIC_KEY_VALUE\\\"\\n            - name: MONGO_CLUSTER_PRIVATE_KEY\\n              value: \\\"MONGO_CLUSTER_PRIVATE_KEY_VALUE\\\"\\n            - name: SEQUENCE\\n              value: parallel\\n        probe: []\\n  annotationCheck: \\\"false\\\"\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"-file=/tmp/chaosengine-ps-custom-chaos-1ap.yaml\",\n            \"-saveName=/tmp/engine-name\"\n          ],\n          \"image\": \"litmuschaos/litmus-checker:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"revert-chaos\",\n        \"container\": {\n          \"image\": \"litmuschaos/k8s:2.9.0\",\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"args\": [\n            \"kubectl delete chaosengine -l 'instance_id in (95c952f9-f530-4910-a6e7-dfb24aa67039, )' -n {{workflow.parameters.adminModeNamespace}} \"\n          ]\n        }\n      }\n    ],\n    \"podGC\": {\n      \"strategy\": \"OnWorkflowCompletion\"\n    }\n  }\n}",
                "cronSyntax": "",
                "workflowName": "updated_workflow_name",
                "workflowDescription": "Custom Chaos Workflow",
                "isCustomWorkflow": isCustomWorkflow,
                "weightages": [
                    {
                        "experimentName": "ps-custom-chaos-1ap",
                        "weightage": 10
                    }
                ],
                'projectID': 'updated_project_id',
                'clusterID': 'updated_cluster_id',
            }
        },
        "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
    }

    ## replacing values
    updated_workflow_manifest_str = data['variables']['request']['workflowManifest'].replace(
        'updated_workflow_name', workflow_name) \
        .replace('ELASTIC_CACHE_NODE_GROUP_ID_VALUE', elastic_cache_node_group_id_value) \
        .replace('ELASTIC_CACHE_REPLICATION_GROUP_ID_VALUE', elastic_cache_replication_group_id_value) \
        .replace('ELASTIC_CACHE_AWS_REGION_VALUE', elastic_cache_aws_region_value) \
        .replace('AWS_SECRET_ACCESS_KEY_VALUE', aws_secret_access_key_value) \
        .replace('CUSTOM_EXPERIMENT_NAME_VALUE', custom_experiment_name_value) \
        .replace('KAFKA_AWS_REGION_VALUE', kafka_aws_region_value) \
        .replace('KAFKA_CLUSTER_ARN_VALUE', kafka_cluster_arn_value) \
        .replace('AWS_ACCESS_KEY_ID_VALUE', aws_access_key_id_value) \
        .replace('MONGO_ATLAS_CLUSTER_URL_VALUE', mongo_atlas_cluster_url_value) \
        .replace('MONGO_CLUSTER_PRIVATE_KEY_VALUE', mongo_cluster_private_key_value) \
        .replace('MONGO_CLUSTER_PUBLIC_KEY_VALUE', mongo_cluster_public_key_value)

    # TOTAL_CHAOS_DURATION, AWS_ROLE_ARN, FORCE
    updated_workflow_name_str = data['variables']['request']['workflowName'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['request']['projectID'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['request']['clusterID'].replace('updated_cluster_id', cluster_id)

    # Inserting updated values
    data['variables']['request']['workflowManifest'] = updated_workflow_manifest_str
    data['variables']['request']['workflowName'] = updated_workflow_name_str
    data['variables']['request']['projectID'] = project_id_str
    data['variables']['request']['clusterID'] = cluster_id_str

    return json.dumps(data)

################################################################################################################

def execute_ps_custom_experiment(experiment_name):
    print("running execute_ps_custom_experiment")
    response = get_auth_token()

    access_token = response.json()['access_token']

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}
    workflow_name = 'ps-custom-chaos-workflow-' + get_random_number()
    json_data = get_ps_custom_experiment_body(workflow_name, experiment_name)

    ps_custom_chaos_workflow_response = requests.post(LITMUS_URL + '/api/query',
                                                      data=json_data, headers=headers)
    print(ps_custom_chaos_workflow_response.status_code)
    print(ps_custom_chaos_workflow_response.json())



############################################################################################################
def terminate_mongo_atlas_instance():
    mongo_atlas = config_data_res['mongo_atlas']
    pub_key = mongo_atlas['pub_key']
    private_key = mongo_atlas['private_key']
    mongodb_atlas_url = mongo_atlas['atlas_url']

    experiment_status = 'Failed'
    response = requests.post(
        mongodb_atlas_url
        , auth=HTTPDigestAuth(pub_key, private_key))
    print(response)

    if response.status_code == 200:
        experiment_status = 'Succeeded'
    
    print('experiment_status :' , experiment_status)

#############################################################################################################
def get_random_number():
    return random.randint(99, 99999999).__str__()


#############################################################################################################
def load_config_file():
    config_file_name = read_config_file()
    file = open(config_file_name)
    config_data = json.load(file)
    return config_data


#############################################################################################################
def read_config_file():
    env = os.environ['DEPLOYMENT_ENV']
    project = os.environ['Project']
    print('PROJECT NAME : ' + project)
    print('ENV NAME : ' + env)
    json_config_path = os.path.join(sys.path[0], project + "/" + "config_" + env + ".json")
    return json_config_path

############################################################################################################

if __name__ == '__main__':

    config_data_res = load_config_file()
    litmus_config = config_data_res['litmus']
    mongo_atlas = config_data_res['mongo_atlas']
    kafka = config_data_res['kafka']
    redis = config_data_res['redis']
    LITMUS_URL = litmus_config['litmus_url']

    pod_delete_config = config_data_res['pod_delete']
    TOTAL_CHAOS_DURATION = pod_delete_config['total_chaos_duration']
    CHAOS_INTERVAL = pod_delete_config['chaos_interval']
    PODS_AFFECTED_PERCENTAGE = pod_delete_config['pods_affected_percentage']
    APP_NAME = pod_delete_config['eks_pod']

    latency_delete_config = config_data_res['pod_nw_slowness']
    TOTAL_CHAOS_DURATION_LATENCY = latency_delete_config['total_chaos_duration']
    NETWORK_LATENCY = latency_delete_config['latency']
    PODS_AFFECTED_PERCENTAGE_LATENCY = latency_delete_config['pods_affected_percentage']
    APP_NAME_LATENCY = latency_delete_config['eks_pod']

    LITMUS_USERNAME = litmus_config['username']
    LITMUS_PASSWORD = litmus_config['password']
    # LITMUS_USERNAME = os.environ['litmus_username']
    # LITMUS_PASSWORD = os.environ['litmus_password']
    experiment_type = os.environ['experiment_type']
    LITMUS_PROJECT_ID = litmus_config['litmus_project_id']
    LITMUS_CLUSTER_ID = get_cluster_id()

    # print(litmus_config)
    # print(LITMUS_USERNAME)
    # print(LITMUS_PASSWORD)
    # print(experiment_type)
    # print(LITMUS_PROJECT_ID)
    # print(LITMUS_CLUSTER_ID)
    

    print("Selected Experiment Type :" + experiment_type)

    if experiment_type == 'ALL':
        print(experiment_type)
        execute_pod_kill_experiment()
        execute_network_latency_experiment()
        execute_ps_custom_experiment('KAFKA')
        execute_ps_custom_experiment('REDIS')
        # terminate_mongo_atlas_instance()
    elif experiment_type == 'POD_TERMINATION':
        print(experiment_type)
        execute_pod_kill_experiment()
    elif experiment_type == 'NETWORK_LAG':
        print(experiment_type)
        execute_network_latency_experiment()
    elif experiment_type == 'ATLAS':
        print(experiment_type)
        execute_ps_custom_experiment(experiment_type)
        # terminate_mongo_atlas_instance()
    elif experiment_type == 'KAFKA':
        print(experiment_type)
        execute_ps_custom_experiment(experiment_type)
    elif experiment_type == 'REDIS':
        print(experiment_type)
        execute_ps_custom_experiment(experiment_type)
    else:
        print("Please enter valid choice[ALL, POD_TERMINATION, NETWORK_LAG, ATLAS, ] ")
