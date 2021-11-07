import pytest
import subprocess
import time
import schemathesis

server_process = subprocess.Popen(["python3", "server_run.py"])
engine_process = subprocess.Popen(["python3", "engine_run.py"])
time.sleep(1)

schema = schemathesis.from_uri("http://localhost:5000/swagger.json")


@pytest.fixture(scope='module')
def setupServer(request):
    def serverTeardown():
        server_process.kill()
        engine_process.kill()
    request.addfinalizer(serverTeardown)


@schema.parametrize()
def test_api(case, setupServer):
    case.call_and_validate()


