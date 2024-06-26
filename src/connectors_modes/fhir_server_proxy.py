from flask import Flask, json, request
from kubernetes import client, config
from pick import pick
from datetime import datetime
import os
import copy
import logging
import os, providers.fhir_provider

logger = logging.getLogger(__name__)
app = Flask(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT")
try:
    MODE_HAPI_FHIR_SERVER_PROXY_SERVERS_LIST = json.loads(os.getenv("MODE_HAPI_FHIR_SERVER_PROXY_SERVERS_LIST"))
except:
    pass

try:
    config.load_kube_config(context='microk8s@GH-Development')
except:
    config.load_incluster_config()

apps_v1 = client.AppsV1Api()
batch_v1 = client.BatchV1Api()
namespace = "default"
print("LOADED CONFIG")
def run():
    
    app.run(host='0.0.0.0')


@app.route('/', methods=['POST'])
def fhir_search():
    body = json.loads(request.data)
    print(MODE_HAPI_FHIR_SERVER_PROXY_SERVERS_LIST)
    final_response = []
    for server_url in MODE_HAPI_FHIR_SERVER_PROXY_SERVERS_LIST:
        print(server_url)
        fhir_provider_source = providers.fhir_provider.FhirProvider(server_url)
        response = fhir_provider_source.generic_search(body)
        final_response.append(response.json())
    
    # Merge all responses in a single one 
    response = final_response[0]
    for i in range(1, len(final_response)):
        response["entry"] += final_response[i]["entry"]
    
    return response
    
@app.route('/connectors/list', methods=['GET'])
def list_connectors():
    # List Deployments
    connectors_list = []
    
    for cronjob in batch_v1.list_namespaced_cron_job(namespace).items:
        print("Name: %s, Schedule: %s" % (cronjob.metadata.name, cronjob.spec.schedule))
        # Check if the cronjob has the label "eu.gravitate-health.fosps.connector: "true"
        try:
            for label in cronjob.metadata.labels:
                if label == "eu.gravitate-health.fosps.connector" and cronjob.metadata.labels[label] == "true":
                    connectors_list.append(cronjob.metadata.name)
        except:
            pass
    return connectors_list


@app.route('/connectors/<connector_name>/run', methods=['POST'])
def run_connector(connector_name: str):
    # Try getting the cronjob with the name connector_name
    # Debug reuqest
    print("Requested running connector: " + connector_name)
    job = None
    try:
        cronjob = batch_v1.read_namespaced_cron_job(connector_name, namespace)
        print("Name: %s, Schedule: %s" % (cronjob.metadata.name, cronjob.spec.schedule))
        # Check if the cronjob has the label "eu.gravitate-health.fosps.connector: "true"
        try:
            for label in cronjob.metadata.labels:
                if label == "eu.gravitate-health.fosps.connector" and cronjob.metadata.labels[label] == "true":
                    job_name = cronjob.metadata.name + "-api-triggered"
                    job_manifest = client.V1Job(
                        metadata=client.V1ObjectMeta(
                            name=f"{job_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        ),
                        spec=copy.deepcopy(cronjob.spec.job_template.spec)
                    )
                    print("Creating job with name: " + job_name)
                    print("Manifest :")
                    print(job_manifest)
                    job = batch_v1.create_namespaced_job(namespace=namespace, body=job_manifest)
                    print(f"Job {job.metadata.name} created to trigger CronJob {job_name} immediately.")

        except Exception as e:
            logger.error("Error creating job", exc_info=True)
            logger.error(e)
            
    except:
        pass
    if job is None:
        # Return 404
        return "Connector not found", 404
    else:
        return f"Connector {connector_name} triggered", 200
