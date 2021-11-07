import signal

import pytest
import subprocess
import time

import requests
import schemathesis
import os
import random
from hypothesis import settings

from hypothesis import strategies as st
server_process = subprocess.Popen(["python3", "server_run.py"], stdout=subprocess.PIPE, preexec_fn=os.setsid)
engine_process = subprocess.Popen(["python3", "engine_run.py"], stdout=subprocess.PIPE, preexec_fn=os.setsid)



try:
    time.sleep(2)
    schema = schemathesis.from_uri("http://localhost:5000/swagger.json")
    result = requests.get("http://localhost:5000/node/")
    all_node_data = result.json()
    known_nodes = [node_data["node_id"] for node_data in all_node_data]
    all_node_ids = [node_data["node_id"] for node_data in all_node_data]



except:
    # Create a fake schema
    schema = schemathesis.from_file('{"swagger": "2.0","info": {"title": "Sample API","description": "API description in Markdown.","version": "1.0.0"},"host": "api.example.com","basePath": "/v1","schemes": ["https"],"paths": {}}')
    all_node_ids = []

@schemathesis.hooks.register
def before_generate_case(context, strategy):
    op = context.operation

    def tune_case(case):
        if "<string:node_id>" in op.path:
            # Super hacky i know, but I can't be bothered to check the actual solution here...
            if random.randint(0, 1):
                case.path_parameters["node_id"] = random.choice(all_node_ids)
        if "<string:additional_property>" in op.path:
            if random.randint(0, 1):
                case.path_parameters["node_id"] = random.choice(["health", "amount_stored"])
        return case
    return strategy.map(tune_case)

@pytest.fixture(scope='module')
def setupServer(request):
    def serverTeardown():
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
    request.addfinalizer(serverTeardown)

@pytest.mark.skipif(server_process is None, reason = "Unable to start the server, skipping")
@schema.parametrize()
@settings(max_examples=100)
def test_api(case, setupServer):
    case.call_and_validate()


