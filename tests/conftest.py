import pytest
import os
import signal


# Yeah, this is hacky af. Since the pytest_terminal_summary is pretty much the last thing that gets done, we want to
# make absolutely sure that the servers we started for the serverAPI test get killed. That should have already happend
# but if we skipped the test (because we only wanted to run a few tests) the subprocesses would never be killed.
@pytest.hookimpl()
def pytest_terminal_summary():
    if pytest.server_process:
        os.killpg(os.getpgid(pytest.server_process.pid), signal.SIGTERM)
    if pytest.engine_process:
        os.killpg(os.getpgid(pytest.engine_process.pid), signal.SIGTERM)