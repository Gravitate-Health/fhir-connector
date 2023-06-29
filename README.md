
FHIR-CONNECTOR 
=================================================

![Latest release](https://img.shields.io/github/v/release/Gravitate-Health/fhir-connector)
![Actions workflow](https://github.com/Gravitate-Health/fhir-connector/actions/workflows/cicd.yml/badge.svg)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache)


Table of contents
-----------------

- [FHIR-CONNECTOR](#fhir-connector)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Deployment](#deployment)
      - [Docker](#docker)
      - [Kubernetes](#kubernetes)
  - [Usage](#usage)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [Getting help](#getting-help)
  - [Contributing](#contributing)
  - [License](#license)
  - [Authors and history](#authors-and-history)
  - [Acknowledgments](#acknowledgments)


Introduction
------------
This reporistory includes a first approach to a tool capable of transforming information from different sources into FHIR format.

The following sections in the README document help to install and deploy the connector and understand how the transformation tool has been developed.

Features
------------
- Syncs [HL7 Gravitate Health ePI repository](https://github.com/hl7-eu/gravitate-health). Uploads ePI in [this folder](https://github.com/hl7-eu/gravitate-health/tree/master/input/fsh) as bundles to FHIR server.
- Syncs [HL7 Gravitate Health IPS repository](https://github.com/hl7-eu/gravitate-health-ips). Uploads IPS in [this folder](https://github.com/hl7-eu/gravitate-health-ips/tree/master/input/fsh) as bundles to FHIR server.

Installation
------------

### Requirements

First, install requierements:
```bash
pip install -r requirements.txt
```

And run the application:
```bash
python3 app.py
```

Optionally, you can create a `.env` file and change the following environment variables:

| Task          	| Description                                                 	| Possible values                       	|
|---------------	|-------------------------------------------------------------	|---------------------------------------	|
| EPI_REPO      	| https://github.com/hl7-eu/gravitate-health.git              	|                                       	|
| IPS_REPO      	| https://github.com/hl7-eu/gravitate-health-ips.git          	|                                       	|
| EPI_SERVER    	| https://fosps.gravitatehealth.eu/epi/api/fhir               	|                                       	|
| IPS_SERVER    	| https://fosps.gravitatehealth.eu/ips/api/fhir               	|                                       	|
| IPS_WHITELIST 	| [Bundle-gravitate-Alicia.json, Bundle-gravitate-Pedro.json] 	|                                       	|
| LOG_LEVEL     	| INFO                                                        	| CRITICAL, ERROR, WARNING, INFO, DEBUG 	|
### Deployment

The deployment of the app can be done in Docker or kubernetes.

#### Docker

```bash
git clone https://github.com/Gravitate-Health/fhir-connector
cd fhir-connector
docker build . -t YOUR_IMAGE_NAME
docker run YOUR_IMAGE_NAME
```

#### Kubernetes

```bash
kubectl apply -f kubernetes/fhir-connector-configmap.yaml
kubectl apply -f kubernetes/fhir-connector-cronjob.yaml
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

Acknowledgments
---------------------------
- [HAPI FHIR](https://hapi.fhir.org/)
- [FHIR SERVER REPOSITORY](https://github.com/hapifhir/hapi-fhir-jpaserver-starter)