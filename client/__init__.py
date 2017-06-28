# coding=utf-8
# __init__.py
# import os
# Enable the required Python libraries for working with Cloudant.
# from cloudant.account import Cloudant
import cloudant.client
from flask import Flask

# from time import gmtime, strftime

# from cloudant.error import CloudantException
# from cloudant.result import Result, ResultByKey
# from cloudant.document import Document

VCAP_SERVICES = {
    "cloudantNoSQLDB": [
        {
            "credentials": {
                "username": "96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix",
                "password": "a48cec1e622bb0dedc3b07c5443c2176c4e9f3ac2fcde2102fb3749132140173",
                "host": "96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix.cloudant.com",
                "port": 443,
                "url": "https://96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix:a48cec1e622bb0dedc3b07c5443c2176c4e9f3ac2fcde2102fb3749132140173@96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix.cloudant.com"
            },
            "syslog_drain_url": 0,
            "label": "cloudantNoSQLDB",
            "provider": 0,
            "plan": "Lite",
            "name": "iot-nongnghiep-NoSQL DB",
            "tags": [
                "data_management",
                "ibm_created",
                "lite",
                "ibm_dedicated_public"
            ]
        }
    ]
}

vcap_servicesData = VCAP_SERVICES
cloudantNoSQLDBData = vcap_servicesData['cloudantNoSQLDB']
credentials = cloudantNoSQLDBData[0]
credentialsData = credentials['credentials']
serviceUsername = credentialsData['username']
servicePassword = credentialsData['password']
serviceURL = credentialsData['url']
db = cloudant.client.Cloudant(serviceUsername, servicePassword, url=serviceURL)

app = Flask(__name__)

import client.welcome
import client.api
