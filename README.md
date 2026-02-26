
# FHIR-CONNECTOR

![Latest release](https://img.shields.io/github/v/release/Gravitate-Health/fhir-connector)
![Actions workflow](https://github.com/Gravitate-Health/fhir-connector/actions/workflows/cicd.yml/badge.svg)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache)


## Table of contents

- [FHIR-CONNECTOR](#fhir-connector)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Active deployments in FOSPS - Gravitate Health](#active-deployments-in-fosps---gravitate-health)
    - [GIT\_FSH HL7 EPI resources](#git_fsh-hl7-epi-resources)
    - [GIT\_FSH HL7 IPS resources](#git_fsh-hl7-ips-resources)
  - [Environment variables](#environment-variables)
    - [Environment variables for working mode: GIT\_FSH](#environment-variables-for-working-mode-git_fsh)
    - [Environment variables for working mode: HAPI\_FHIR\_SERVER\_SYNC](#environment-variables-for-working-mode-hapi_fhir_server_sync)
    - [Environment variables for working mode: FHIR\_SERVER\_PROXY](#environment-variables-for-working-mode-fhir_server_proxy)
    - [Environment variables for working mode: SMM\_TOOL](#environment-variables-for-working-mode-smm_tool)
  - [Deployment](#deployment)
    - [Local deployment](#local-deployment)
    - [Deployment](#deployment-1)
      - [Docker](#docker)
      - [Kubernetes (Kustomize)](#kubernetes-kustomize)
  - [Usage](#usage)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [Getting help](#getting-help)
  - [Contributing](#contributing)
  - [License](#license)
  - [Authors and history](#authors-and-history)
  - [Acknowledgments](#acknowledgments)


## Introduction

This repository includes an implementation for a tool capable of transforming information from different sources into FHIR format. The connector has different working modes, and the desired one must be specified. The following working modes are currently available:
- fhs-git: pulls a git repository containing .fsh files, converts them to JSON format and uploads them to the specified HAPI FHIR server.
- HAPI FHIR sync: pulls resources from a HAPI FHIR server and writes them to the specified FHIR server.
- HAPI FHIR proxy: the connector acts as a proxy for FHIR resources. When a resource is requested to the connector, it will look for the resource in all the FHIR sources it has available.

The following sections in the README document help to install and deploy the connector and understand how the transformation tool has been developed.


## Active deployments in FOSPS - Gravitate Health


### GIT_FSH HL7 EPI resources

- Syncs [HL7 Gravitate Health ePI repository](https://github.com/hl7-eu/gravitate-health). Uploads ePI in [this folder](https://github.com/hl7-eu/gravitate-health/tree/master/input/fsh) as bundles to FHIR server.


### GIT_FSH HL7 IPS resources

- Syncs [HL7 Gravitate Health IPS repository](https://github.com/hl7-eu/gravitate-health-ips). Uploads IPS in [this folder](https://github.com/hl7-eu/gravitate-health-ips/tree/master/input/fsh) as bundles to FHIR server.


## Environment variables

The following environment variables must be set:

| Task          	    | Description                                                 	| Possible values                       	          |
|---------------    	|-------------------------------------------------------------	|---------------------------------------	          |
| CONNECTOR_MODE     	| Working mode of the connector                               	| GIT_FSH, HAPI_FHIR_SERVER_SYNC, FHIR_SERVER_PROXY 	    |
| WHITELIST         	| List of resources to get, if not all should be retrieved     	| ["resource1.json", "resource2.json"]   	          |
| DESTINATION_SERVER  | URL of the destination FHIR server                          	|                                       	          |
| LOG_LEVEL         	| Log level                                                    	| CRITICAL, ERROR, WARNING, INFO, DEBUG  	          |
| EMAIL_ENABLED       | Enable sending of emails with the results of the connector   	| true                                              |
| EMAIL_SENDER        | Email address of the sender                                 	|                                        	          |
| EMAIL_PASSWORD      | Must be set as a base64 encoded secret                       	|                                        	          |
| EMAIL_SMTP_SERVER   | SMTP server address                                         	|                                        	          |
| EMAIL_RECIPIENT     | Email address or list to send the contents                  	|                                        	          |

The environment `EMAIL_PASSWORD` must be set via k8s secret:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fhir-connector-email-password
data:
  password: BASE64_ENCODED_PASSWORD
```

### Environment variables for working mode: GIT_FSH


| Task          	                   | Description                                                 	| Possible values                       	          |
|----------------------------        |-------------------------------------------------------------	|---------------------------------------	          |
| CONNECTOR_MODE 	                   | Working mode of the connector                               	| GIT_FSH                                      	    |
| MODE_GIT_FSH_SOURCE_REPO           | URL of the git repository                                   	|                                       	          |
| MODE_GIT_FSH_SOURCE_REPO_BRANCH    | Branch to pull                                             	| "main", "development", etc.            	          |


### Environment variables for working mode: HAPI_FHIR_SERVER_SYNC

| Task          	                    | Description                                                 	| Possible values                       	          |
|----------------------------         |-------------------------------------------------------------	|---------------------------------------	          |
| CONNECTOR_MODE 	                    | Working mode of the connector                               	| HAPI_FHIR_SERVER_SYNC                            	    |
| MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER | URL of the FHIR server                                       	|                 	                                |
| MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES     | ["Bundle", "Patient", "Observation", etc.]                   	|                                       	          |


### Environment variables for working mode: FHIR_SERVER_PROXY

| Task          	            | Description                                                 	| Possible values                       	          |
|---------------------------- |-------------------------------------------------------------	|---------------------------------------	          |
| CONNECTOR_MODE 	            | Working mode of the connector                               	| GIT_FSH, HAPI_FHIR_SERVER_SYNC, FHIR_SERVER_PROXY 	    |
| SOURCE_SERVER_LIST          | ["https://fhir-server1.com", "https://fhir-server2.com"]     	|                                       	          |
| DESTINATION_SERVER        	| http://fhir-server-epi:8080/epi/api/fhir               	|                                       	          |


### Environment variables for working mode: SMM_TOOL

| Task          	            | Description                                                 	| Possible values                       	          |
|---------------------------- |-------------------------------------------------------------	|---------------------------------------	          |
| CONNECTOR_MODE 	            | Working mode of the connector                               	| SMM_TOOL                                     	    |
| DESTINATION_SERVER        	| http://fhir-server-epi:8080/epi/api/fhir               	|                                       	          |
| SMM_SERVER_URL              | https://budibase.gravitate-health.lst.tfo.upm.es/api/public/v1|                                       	          |
| SMM_APP_ID                	| Budibase app id                                              	|                                       	          |
| SMM_TABLE_ID              	| Budibase table id                                            	|                                       	          |
| SMM_API_KEY               	| Read from k8s secret                                         	|                                       	          |

To create API KEY secret: 
```bash
kubectl create secret generic budibase-smm-api-key-secret --from-literal=apikey=API_KEY_STRING
```
kubectl create secret generic budibase-smm-api-key-secret --from-literal=apikey=363d4adf8234c7ac0a9e9a356addd061-c544898c110bd82ee96436d2b95039fc3d84690af962993bf1f196951653f9d0444ad1e8abaff19d

## Deployment

### Local deployment

First, install requierements:
```bash
pip install -r requirements.txt
```

And run the application:
```bash
python3 app.py
```

To deploy locally, you can create a `.env` file and change the environment variables.


### Deployment

The deployment of the app can be done in Docker or kubernetes.

#### Docker

```bash
git clone https://github.com/Gravitate-Health/fhir-connector
cd fhir-connector
docker build . -t YOUR_IMAGE_NAME
docker run YOUR_IMAGE_NAME
```

#### Kubernetes (Kustomize)

Production: 
```bash
kubectl apply -k kubernetes/base
```

Development: 
```bash
kubectl apply -k kubernetes/dev
```


Usage
-----

Known issues and limitations
----------------------------

Getting help
------------
In case you find a problem or you need extra help, please use the issues tab to report the issue.

Contributing
------------
To contribute, fork this repository and send a pull request with the changes squashed.

License
-------
This project is distributed under the terms of the [Apache License, Version 2.0 (AL2)](https://www.apache.org/licenses/LICENSE-2.0).  The license applies to this file and other files in the [GitHub repository](https://github.com/Gravitate-Health/fhir-connector) hosting this file.

```
Copyright 2022 Universidad Politécnica de Madrid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
Authors and history
---------------------------
- Guillermo Mejías ([@gmej](https://github.com/gmej))
- Isabel Varona ([@isabelvato](https://github.com/isabelvato))
- Alejandro Alonso ([@aalonsolopez](https://github.com/aalonsolopez))

Acknowledgments
---------------------------
- [HAPI FHIR](https://hapi.fhir.org/)
- [FHIR SERVER REPOSITORY](https://github.com/hapifhir/hapi-fhir-jpaserver-starter)