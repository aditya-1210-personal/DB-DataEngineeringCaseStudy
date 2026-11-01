from unittest.mock import patch
from orchestration import flow

def test_execute():
    with patch.object(flow.subprocess, "run") as run:
        flow.execute(["echo", "ok"])
        run.assert_called_once()

def test_flow_tasks_are_registered():
    assert flow.generate_data.name == "generate_data"
    assert flow.load_sources.name == "load_sources"
    assert flow.dbt_build.name == "dbt_build"
