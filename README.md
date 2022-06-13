
FHIR-CONNECTOR 
=================================================

[![Latest release](https://img.shields.io/github/v/release/mhucka/readmine.svg&color=b44e88)](https://github.com/mhucka/readmine/releases)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![Build Status](https://travis-ci.org/anfederico/clairvoyant.svg?branch=master)](https://travis-ci.org/anfederico/clairvoyant)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache)


Table of contents
-----------------

- [FHIR-CONNECTOR](#fhir-connector)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Deployment](#deployment)
  - [Usage](#usage)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [Getting help](#getting-help)
  - [Contributing](#contributing)
  - [License](#license)
  - [Authors and history](#authors-and-history)
  - [Acknowledgments](#acknowledgments)


Introduction
------------
This reporistory includes a first approach to a tool capable of transforming information from different sources into FHIR format. However, for the first version, the connector recreates how it works by means of an example of a Patient. 

The following sections in the README document help to install and deploy the connector and understand how the transformation tool has been developed. 

Installation
------------

### Requirements

First of all, because the connector has been developed in Python, we will need a framework to deploy the application. In this case, it have been used _Flask v2.0.2_ for the simplicity and speed. 

At the same time, the development of the code requires the use of the _requests_ library, which is also included in this file. Thanks to this library, GET and POST methods can be executed.

- requirements.txt
  - Flask
  - requests 

### Deployment

The deployment of the app is been explained in the following lines. 

Firstly, is necessary to clone the repository in the command line.  

```bash
git clone _path_
```
After that, the folder with all the documents will be in local. We sholud go to the path where the folder has been saved:

```bash
cd path/fhir-connector
```
Once this has been done, we could deploy the container to run the application. For that: 

```bash
docker build -t _name container_ . 
```
Finally, the container has been created and is time run it. 

```bash
docker run -it -p 5000:5000 _name container_  
```

By executing this command, the service example of the fhir connector will be deploy locally. In the next section, we will explain the way to try it. 

Usage
-----
Once the container is created and running, through the command terminal returns a localhost address where our service is up. The format will be as follows http://127.0.0.x:5000, where the 5000 indicates the port.


![Service fhir connector](./img/fhir.png )

When we open it in the browser we will be able to observe a json in FHIR format, corresponding to a _Patient_. 

In this case, the application _app.py_ has made: 

1. First a GET method from the HAPI server obtaining an example of a patient from the repository. 
   
2. Second a POST method (with the information obtained in the GET) to the FHIR server deployed for the Gravitate Health project. 

Known issues and limitations
----------------------------
The connector explain in the previous sections is an example of how we will work the final fhir-connector in the following MVPs. Therefore, take this code as an approximation of the final result. 

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
- Isabel Varona ([@isabelvato](https://github.com/isabelvato))

Acknowledgments
---------------------------
- [HAPI FHIR](https://hapi.fhir.org/)
- [FHIR SERVER REPOSITORY](https://github.com/hapifhir/hapi-fhir-jpaserver-starter)